from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

@csrf_exempt
def index(request):
    sessionId  = request.POST.get("sessionId")
    serviceCode = request.POST.get("serviceCode")
    phoneNumber = request.POST.get("phoneNumber")
    text = request.POST.get("text")

    def get_ovulation(date_of_next):
        ovulation_date = date_of_next - timedelta(days = 14)
        return datetime.strftime(ovulation_date, '%B %d')
        
    def get_menstruation(date_of_next):
        return datetime.strftime(date_of_next, '%B %d')

    def get_possibility(this_day,ovulation_day):
        difference = ovulation_day - this_day
        if 5 >= difference.days >= -1:
            return "high"
        return "low"

    def get_day_status(this_day,date_of_next):
        #Before ovulation date
        ovulation_date = date_of_next - timedelta(days = 14)
        days_to_ovulation = (ovulation_date - this_day).days + 1
        ovulation_days = ' '+str(days_to_ovulation) if days_to_ovulation != 0 else ''
        plural = 'day to ' if days_to_ovulation == 1 else '' if days_to_ovulation == 0 else 'days to '
        if_day = ' day' if days_to_ovulation == 0 else '' 
        if days_to_ovulation >= 0:
            return "Today is{} {}ovulation{}.".format(ovulation_days,plural,if_day)

        #Before PMS
        pms_date = date_of_next - timedelta(days=3)
        days_to_pms = (pms_date - this_day).days + 1
        plural = '' if days_to_pms == 1 else 's'
        if days_to_pms >= 1:
            return "Today is {} day{} to PMS".format(days_to_pms,plural)

        #PMS
        pms_difference = this_day - pms_date
        if 1 <= pms_difference.days + 1 <= 3:
            return "Today is day {} of PMS".format(pms_difference.days + 1)

        #Expected Menstruation
        if this_day.date() == date_of_next.date():
            return "Today is the expected menstruation day"
        
        day_from = (this_day - date_of_next).days * 1 
        return "This is day {} from the expected menstruation day".format(day_from)

    if request.method == "POST":

        #First message
        if text == '' or not text:
            return HttpResponse("CON Type in the start date of your last Menstrual Period e.g. 31/07/2019")

        #Second message
        if "*" not in text:
            try:
                day,month,year = list(map(lambda x: x.strip(), text.split('/')))
                full_date = '/'.join([day,month])
                old_date = datetime.strptime(full_date, '%d/%m')
            except Exception:
                return HttpResponse("END Invalid input:\n{}".format(text))
            else:
                return HttpResponse("CON How long is your cycle length in days e.g. 28")

        new_text = text.split('*')
        if len(new_text) == 2:
            try:
                #Tried Before
                new_text = text.split('*')
                day,month,year = list(map(lambda x: x.strip(), new_text[0].split('/')))
                
                if len(year) != 4:
                    return HttpResponse("END Invalid input:\n{}".format(new_text[0]))

                full_date = '/'.join([year,month,day])
                old_date = datetime.strptime(full_date, '%Y/%m/%d')

                cycle_length = int(new_text[-1].strip())
                next_date = old_date + timedelta(days = cycle_length)
                today = datetime.now()

                #If a float was entered or if cycle length not acceptable
                if cycle_length != float(new_text[-1].strip()) or not 20 <= cycle_length <= 45:
                    return HttpResponse("END Invalid input: {}".format(cycle_length))
            except Exception:
                return HttpResponse("END Invalid input.")
            else:
                message  = "Today is {}\n".format(datetime.strftime(datetime.now(), "%B %d"))
                message += "1. Ovulation Date: {}\n".format(get_ovulation(next_date))
                message += "2. Next Menstruation Date: {}\n".format(get_menstruation(next_date))
                message += "3. {}\n".format(get_day_status(today, next_date))
                message += "4. Possibility of pregnancy is {}".format(get_possibility(today, next_date - timedelta(days = 14)))
                return HttpResponse("END {}".format(message))

    return HttpResponse("END Unidentified Request")