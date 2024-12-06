from datetime import datetime

def getDate():
    numtoMonths = {1: 'January', 2: 'Feburary', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

    date = str(datetime.today().date())
    monthI = date[5:].find('-') + 5
    monthNum = int(date[5:monthI])
    month = numtoMonths[monthNum]
    day = date[monthI+1:]
    formattedDate = f'{month} {day}, {date[:4]}'
    return date, formattedDate


def recycleClothes(app):
    currDate, _ = getDate()

    with open('week_log.txt', 'r') as file:
        allLines = file.readlines()
    
    for line in allLines:
        lDate = line.split(',')[0] 
        
        format = "%Y-%m-%d"
        date1 = datetime.strptime(currDate, format)
        date2 = datetime.strptime(lDate, format)

        difference = date1-date2
        difference = str(difference)[:2]
        print(difference)
    
        if int(difference) > 7:
            allLines.remove(line)
        
        with open('week_log.txt', 'w') as file:
            for line in allLines:
                file.write(line)
        
        return allLines
        
    

    
print(recycleClothes(None))