import calendar
from datetime import datetime
from dateutil import parser
from TransactionApp.models import Category, Payee, Transaction, UserCategory
from projectApp1.models import Membership
from TransactionApp.__init__ import THIS_MONTH, LAST_MONTH, CUSTOM_RANGE, DEFAULT_START_PAGE, DEFAULT_RPP
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.db.models import Q


def import_from_snapshot():
    import json
    import itertools
    from projectApp1.models import Membership, Group
    from django.contrib.auth.models import User

    json_file = open('mysql_dump_snapsho')
    data = json.load(json_file)
    model_dict = dict()
    # group the json by model
    for key, g in itertools.groupby(data, key=lambda x: x["model"]):
        model_dict[key] = list(g)
    model_strings = ['TransactionsApp.users', 'TransactionsApp.groupstable', 'TransactionsApp.transactions', 'personalApp.categories', 'personalApp.transfers']
    # make a dictionalr of old_pk and new_pk from user model
    user_dict = dict()
    for temp in model_dict[model_strings[0]]:
        try:
            asd = User.objects.create_user(
                                    username=temp['fields']['email'],
                                    email=temp['fields']['email'],
                                    password='p'
                                    )
        except:
            asd = User.objects.get(
                                    username=temp['fields']['email'],
                                    )
        user_dict[str(temp['pk'])] = asd.id   # assign the new id here
    ######## groupstable
    group_dict = dict()
    for temp in model_dict[model_strings[1]]:
        asd = Group.objects.create(
                            name=temp['fields']['name'],
                            description="",
                            privacy=0,
                            deleted=temp['fields']['deleted']
                            )
        for i in temp['fields']['members']:
            Membership.objects.create(
                            group_id=asd.id,
                            user_id=user_dict[str(i)],
                            administrator=False,
                            positions="",
                            amount_in_pool=0,
                            deleted=temp['fields']['deleted']
                            )
        group_dict[str(temp['pk'])] = asd.id   # assign the new id here
    # from transactions table create a list of dictionaries
    for temp in model_dict[model_strings[2]]:
        asd = Transaction.objects.create(
                        paid_user_id=user_dict[str(temp['fields']['user_paid'])],
                        amount=temp['fields']['amount'],
                        description=temp['fields']['description'],
                        transaction_time=temp['fields']['timestamp'],
                        created_by_user_id=user_dict[str(temp['fields']['user_paid'])],
                        created_for_group_id=group_dict[str(temp['fields']['group'])],
                        deleted=temp['fields']['deleted']
                        )
        for i in temp['fields']['users_involved']:
            Payee.objects.create(
                                txn_id=asd.id,                                     # assign id from above
                                user_id=user_dict[str(i)],
                                outstanding_amount=-temp['fields']['amount'] / len(temp['fields']['users_involved']) if i != temp['fields']['user_paid'] else temp['fields']['amount'] - temp['fields']['amount'] / len(temp['fields']['users_involved']),
                                deleted=temp['fields']['deleted']
                                )
    # from categories create categories
    category_dict = dict()
    for temp in model_dict[model_strings[3]]:
        cat = 2 if (temp['fields']['category_type'] == 'leach') else 1
        asd = Category.objects.create(
                    name=temp['fields']['name'],
                    category_type=cat,
                    privacy=0,
                    created_by_id=user_dict[str(7)],
                    )
        category_dict[str(temp['pk'])] = asd.id    # assign the new id here
        UserCategory.objects.create(
                                    user_id=user_dict[str(temp['fields']['userID'])],
                                    category_id=asd.id,
                                    initial_amount=temp['fields']['initial_amt'],
                                    current_amount=0,
                                    deleted=False
                                    )
    # transfers
    for temp in model_dict[model_strings[4]]:
        Transaction.objects.create(
                                paid_user_id=user_dict[str(temp['fields']['userID'])],
                                amount=temp['fields']['amount'],
                                from_category_id=category_dict[str(temp['fields']['fromCategory'])],
                                description=temp['fields']['description'],
                                to_category_id=category_dict[str(temp['fields']['toCategory'])],
                                transaction_time=temp['fields']['timestamp'],
                                created_by_user_id=user_dict[str(temp['fields']['userID'])],
                                deleted=temp['fields']['deleted']
                                )
    # populate the outstanding_amount in Membership
    asd = Group.objects.get(name='PA303')
    for temp_user in asd.members.all():
        temp_mem = Membership.objects.get(group=asd, user=temp_user)
        temp_mem.amount_in_pool = get_outstanding_amount(asd, temp_user)
        temp_mem.save()
    asd = UserCategory.objects.filter().order_by('category__category_type')
    for temp in asd:
        category_lost = Transaction.objects.filter(
                                        from_category_id=temp.id,
                                    ).aggregate(
                                        Sum('amount')
                                    )['amount__sum']
        category_lost = category_lost if category_lost else 0
        category_gained = Transaction.objects.filter(
                                        to_category_id=temp.id,
                                    ).aggregate(
                                        Sum('amount')
                                    )['amount__sum']
        category_gained = category_gained if category_gained else 0
        temp.current_amount = category_gained - category_lost + temp.initial_amount
        temp.save()
    json_file.close()


def get_outstanding_amount(group_id, user_id, end_time=None):
    '''
    get the net outstandin amount in a group till the timestamp specified
    '''
    if end_time is not None:
        time_filter = Q(transaction_time__lte=end_time)
    else:
        time_filter = Q()
    txn_filters = (
                Q(created_for_group_id=group_id) &
                Q(deleted=False) &
                Q(time_filter)
                )
    # Get the net of all the transaction in which user was not a Payee
    # i.e user just paid but did not have any expense towards the txn
    s1 = Transaction.objects.filter(
                        txn_filters
                    ).filter(
                        paid_user_id=user_id
                    ).exclude(
                        users_involved=user_id
                    ).aggregate(
                        Sum('amount')
                    )['amount__sum']
    # Get the net sum of all the expenses the user was a Payee
    s2 = Payee.objects.filter(
                        deleted=False
                    ).filter(
                        user_id=user_id
                    ).filter(
                        txn__id__in=list(Transaction.objects.values_list('id', flat=True).filter(txn_filters))
                    ).aggregate(
                        Sum('outstanding_amount')
                    )['outstanding_amount__sum']
    return s1 + s2


def get_expense(group_id, user_id, start_time, end_time):
    '''
    Helper function to get the expense in the given time frame
    '''
    s2t = sum([temp.get_expense(user_id) for temp in Transaction.objects.filter(
                    Q(created_for_group_id=group_id) &
                    Q(deleted=False) &
                    (Q(paid_user_id=user_id) | Q(users_involved__id__in=[user_id])) &   # for including all transaction to which user is conencted
                    Q(transaction_time__range=(start_time, end_time))
                    ).distinct()])
    return s2t


def parseGET_initialise(request):
    '''
    Helper function to parse the requestGET to
    populate variables
    start_time
    end_time
    timeRange,
    filter_user_id,
    page_no,
    txn_per_page
    '''
    # Defaults
    current_time = datetime.now()
    month_start = datetime(year=current_time.year, month=current_time.month, day=1)
    start_time = month_start
    end_time = current_time
    timeRange = THIS_MONTH                                                                          # for angularjs
    # time range
    if 'tr' in request.GET:
        try:
            if int(request.GET['tr']) == THIS_MONTH:
                start_time = datetime(year=current_time.year, month=current_time.month, day=1)      # end_time is alredy initialised
                timeRange = THIS_MONTH
            elif int(request.GET['tr']) == LAST_MONTH:
                start_time = datetime(year=current_time.year, month=current_time.month - 1, day=1)
                timeRange = LAST_MONTH                                                              # for angularjs
                end_time = datetime(
                            year=current_time.year,
                            month=current_time.month,
                            day=1)
                            #day=calendar.monthrange(current_time.year, current_time.month - 1)[1])
        except:
            # default values alredy filled
            pass
    elif 'ts' in request.GET or 'te' in request.GET:
        try:
            timeRange = CUSTOM_RANGE                                                                # for angularjs
            # time start
            if 'ts' in request.GET:
                start_time = parser.parse(request.GET['ts'])
            # time end
            if 'te' in request.GET:
                end_time = parser.parse(request.GET['te'])
        except:
            # default values alredy filled
            pass
    try:
        filter_user_id = int(request.GET['u'])
    except:
        filter_user_id = request.user.pk
    try:
        page_no = int(request.GET['page'])
    except:
        page_no = DEFAULT_START_PAGE
    try:
        txn_per_page = int(request.GET['rpp'])
    except:
        txn_per_page = DEFAULT_RPP
    return (start_time, end_time, timeRange, filter_user_id, page_no, txn_per_page)


def get_page_info(transaction_list, txn_per_page, page_no):
    # Pagination stuff
    paginator_obj = Paginator(transaction_list, txn_per_page)
    try:
        current_page = paginator_obj.page(page_no)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        current_page = paginator_obj.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        current_page = paginator_obj.page(paginator_obj.num_pages)
    return (paginator_obj, current_page)


def new_group_transaction_event(group_id, transaction):
    '''
    update the Membership table outstanding
    update the GroupCategory table outstanding
    '''
    # get memberships of all users involved
    involved_memberships = Membership.objects.filter(
                                                Q(user_id=transaction.paid_user_id) |
                                                Q(user_id__in=transaction.users_involved.values_list('id', flat=True))
                                            ).filter(
                                                Q(group_id=group_id)
                                            )
    for i in involved_memberships:
        i.amount_in_pool = i.amount_in_pool + transaction.get_outstanding_amount(i.user_id)
        i.save()
    try:
        tc = GroupCategory.objects.get(
                        group_id=group_id,
                        category_id=transaction.to_category_id)
        tc.current_amount = tc.current_amount + transaction.amount
        tc.save()
    except:
        pass
    pass


def new_personal_transaction_event(user_id, transaction):
    '''
    update the UserCategory table outstanding
    '''
    try:
        fc = UserCategory.objects.get(
                        user_id=user_id,
                        category_id=transaction.from_category_id)
        fc.current_amount = fc.current_amount - transaction.amount
        fc.save()
    except:
        pass
    try:
        tc = UserCategory.objects.get(
                        user_id=user_id,
                        category_id=transaction.to_category_id)
        tc.current_amount = tc.current_amount + transaction.amount
        tc.save()
    except:
        pass
    pass