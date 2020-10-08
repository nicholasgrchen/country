import csv, json, requests, re
from bs4 import BeautifulSoup
from pprint import pprint

################## extra credit at end of file ##################



def csv_parser (filename):
    with open(filename+".csv", encoding = "utf8") as fin:
        reader = csv.reader(fin, delimiter = ",")
        readlist = list(reader)
        toReturn = [['Country', 'Region', 'Population','Pop. Density (per sq. mi.)', 'GDP ($ per capita)', 'Literacy (%)']]
        for entry in readlist[1:]:
            newlist = [entry[0].strip(), entry[1].strip(), int(entry[2]), float(entry[4].replace(",", "."))]
            if entry[8] == "":
                newlist.append("Unknown")
            else:
                newlist.append(int(entry[8]))
            if entry[9]=="":
                newlist.append("Unknown")
            else:
                newlist.append(float(entry[9].replace(",", ".")))
            toReturn.append(newlist)
    return toReturn
    #return type list


def json_parser (filename, data):
    #data is the list returned from the csv_parser method above
    with open(filename+".json") as fin:
        jsondict = json.load(fin)
    listofdicts = []
    for entry in data[1:]:
        newdict = {"Country":entry[0], "Region":entry[1], "Population":entry[2], "Pop. Density (per sq. mi.)":entry[3], "GDP ($ per capita)":entry[4], "Literacy (%)": entry[5]}
        newdict["Languages"] = None if jsondict[entry[0]]["languages"] == [] else [lang for lang in jsondict[entry[0]]["languages"].split(";")]
        newdict["National Dish"]= "Unknown" if jsondict[entry[0]]["national_dish"]==None else jsondict[entry[0]]["national_dish"]
        newdict["Religion"]= "Unknown" if jsondict[entry[0]]["religion"]==None else jsondict[entry[0]]["religion"]
        newdict["Government"]= "Unknown" if jsondict[entry[0]]["government"]==None else jsondict[entry[0]]["government"]
        newdict["Currency Name"]= "Unknown" if jsondict[entry[0]]["currency_name"]==None else jsondict[entry[0]]["currency_name"]
        listofdicts.append(newdict)
    listofdicts.sort(key = lambda x:x["Country"])
    return listofdicts

def company_parser (filename, data):
    #data is the list returned from the json_parser method above
    with open(filename+".csv", encoding = "utf8") as fin:
        reader = csv.reader(fin, delimiter = ",")
        companieslist = list(reader)
    newdict = {}
    for country in data:
        countryname=" ".join([word.capitalize() for word in country["Country"].split()])
        newdict[countryname] = {"GDP ($ per capita)":country["GDP ($ per capita)"]}
        companylist=[]
        industrieslist=[] #remember to check for duplicates later
        estemp = 0
        for business in companieslist:
            if " ".join([word.capitalize() for word in business[7].split()])==country["Country"]:
                companylist.append(" ".join([word.capitalize() for word in business[1].split()]))
                industrieslist.append(business[4])
                estemp+= int(business[10])
        industrieslist = list(set(industrieslist))
        newdict[countryname]["businesses"]=companylist
        newdict[countryname]["industries"]=industrieslist
        newdict[countryname]["estimated_employees"]=estemp
    #add those without a listed country below:
    newdict["Unknown"]={"GDP ($ per capita)":0}
    companylist=[]
    industrieslist=[]
    esttemp=0
    for business in companieslist[1:]:
        if " ".join([word.capitalize() for word in business[7].split()]) not in newdict.keys():
            companylist.append(" ".join([word.capitalize() for word in business[1].split()]))
            industrieslist.append(business[4])
            esttemp+= int(business[10])
    industrieslist = list(set(industrieslist))
    newdict["Unknown"]["businesses"]=companylist
    newdict["Unknown"]["industries"]=industrieslist
    newdict["Unknown"]["estimated_employees"]=esttemp
    return newdict
    #return dict

def country_stats (json_filename, txt_filename, data):
    #first two parameters are files that will be written to
    with open(json_filename+".json", "w") as fout1:
        json.dump(data, fout1, indent = 4)
    countries = list(data.keys())
    countries.sort()
    toWrite=""
    for country in countries:
        toWrite+=f"{country} has a total of {str(len(data[country]['businesses']))} businesses, an estimated {str(data[country]['estimated_employees'])} employees, a total of {str(len(data[country]['industries']))} industries, and total GDP of {str(data[country]['GDP ($ per capita)'])}.\n"
    #toWrite=toWrite[:-1] removed because apparently we did not need to account for this per the autograder
    with open(txt_filename+".txt", "w") as fout:
        fout.write(toWrite)
    #third parameter is the dict returned by company_parser
    return "Data successfully exported."
    #write data from company_parser to json_filename
    #write to txt_filename in the format “{country} has a total of {number of businesses} businesses, anestimated {number of employees} employees, a total of {number ofindustries} industries, and total GDP of {GDP}.”
    #then, return string saying "Data successfully exported."

def inequality (region, gini_val):
    response = requests.get("https://restcountries.eu/rest/v2/region/"+region)
    if response.status_code==404:
        return "The given region was not found"
    else:
        newdict={}
        for country in response.json():
            if country["gini"]!=None and country["gini"]>gini_val:
                newdict[country["name"]]=country["gini"]
        return newdict
    #pprint(response.json())
    #return a dictionary mapping a country's name (if country is in region) to it's gini coefficient if the coefficient is higher than gini_val
    #use REST countries API for the function
    #if the specified region is not a valid region in the API, return "The given region was not found"
    #pass
    #return a dict

def html_parser (filename):
    with open(filename+".html") as fin:
        htmlreader = fin.read()
    soup = BeautifulSoup(htmlreader, "lxml")
    tables = soup.find_all('table')
    exports = tables[1]
    imports = tables[2]
    exportdata = exports.find_all('tr')
    exptable=[[str(exportdata[0].findAll('th')[i].contents[0]) for i in range(0,4)]]
    for entry in exportdata[3:]:
        col1 = entry.findAll('td')[0].contents
        col2 = entry.findAll('td')[1].contents
        col3 = entry.findAll('td')[2].contents
        col4 = entry.findAll('td')[3].contents
        rank=int(col1[0][:-1])
        country= re.search(r'>.*</a', str(col2))[0][1:-3]
        export= float(re.search(r'\S+', col3[0])[0])
        pct= re.search(r'\S+', col4[0])[0]
        exptable.append([rank, country, export, pct])
    importdata = imports.find_all('tr')
    imptable=[[str(importdata[0].findAll('th')[i].contents[0]) for i in range(0,4)]]
    for entry in importdata[3:]:
        col1 = entry.findAll('td')[0].contents
        col2 = entry.findAll('td')[1].contents
        col3 = entry.findAll('td')[2].contents
        col4 = entry.findAll('td')[3].contents
        rank=int(col1[0][:-1])
        country= re.search(r'>.*</a', str(col2))[0][1:-3]
        export= float(re.search(r'\S+', col3[0])[0])
        pct= re.search(r'\S+', col4[0])[0]
        imptable.append([rank, country, export, pct])
    return (exptable, imptable)

    #print(first_column)
    #pprint(exports)
    #print(teheader)
    #re.match()
    #use inspect element to identify the source code easily

    #for tr in soup.find()
    #return[] #ignore now, just testing code above
    #return a tuple

#pprint(country_stats("testout.json", "testout.txt", company_parser("companies.csv", json_parser("additional_stats.json", csv_parser("countries.csv")))))
#print(inequality("Mars", 73.9))
#print(html_parser("foreign_trade"))

def bonus (filenamein, toptraders, exportoutput, importoutput, year):
    """
    Question this method answers:
    Of the top 15 import/export partners for the current year, during which months of a specific previous year are the given countries most active?
    How do each country's relative quantities of imports and exports compare to each other?
    How active is trade with a particular country in a given month, relative to another month, for that particular country?


    Purpose of this method:
    This function takes in the tuple returned by html_parser (in doing so using the foreign_trade.html file) as toptraders
    and a csv file from the US Census Bureau of import/export monthly data by country as filenamein
    It then identifies the top 15 countries from toptraders (for imports and exports) and collects data for those countries from the input csv
    Method will calculate each month's imports/exports as a percentage of the YTD total for top 15 importers/exporters for the specified year (as far back as 1985). Percentages are rounded to the nearest thousandth of a percent.
    List of percentages is written to a CSV file - one CSV file for top 15 importers, one for top 15 exporters.
    For readability, it is better to open the CSV in Microsoft Excel. However, for some reason, Excel formats cells to display 2 decimal places by default. 3 decimal places can be seen in the formula bar when clicking on the cell.
    NOTES:
        The source of the csv is from the same site as the one that provided the HTML file to be scraped in html_parser, so much of the data in the html file provided for this assignment can be obtained from the csv file I located.
        However, it is still necessary to use both files because the CSV contains regions in addition to countries, so a strict definition of top 15 countries (from html_parser) is needed
        Note also: though html_parser provides YTD totals, this data is only updated through July 2020, while the csv provides data through August 2020, so the csv is used to calculate totals.
        In essence, taking in the tuple of lists from html_parser simply determines which countries will be used as the top 15.
        Once these countries are identified, all data about them are sourced directly from the CSV file.

    Insightfulness of this method:
    When writing this method, a particular application that came to mind was predicting future imports and exports, such that sufficient resources could be provided.
    For instance, if you had the Year-to-date totals for top 15 importing and exporting countries (provided by the html webpage, parsed by html_parser, and passed to this method as "toptraders"),
    you could then look at historical data (from past years in the csv file) to see when these countries import/export more.
    For instance, Mexico tends to have a greater percentage of trade during summer leading into fall months (but not as much in the winter months), which *could* be a result of them being a major agricultural partner of the United States.
    This would be useful to logistics firms who might want to adjust more capacity to Mexico during that time of year, or to Customs and Border Patrol, who might staff more agents to commercial import lanes at Mexican ports-of-entry during that time.

    Example method call (commented out to not break autograder):
    bonus("country", html_parser("foreign_trade"), "bonusexport", "bonusimport", 2019)
    Uses the country.csv file (from Census Bureau, file attached) for trade data per country, broken down by month.
    Uses tuple returned from html_parser, which itself is run on the foreign_trade.html site, scraped for top 15 importers/exporters of 2020 (thus far).
    Writes export data to bonusexport2019.csv and import data to bonusimport2019.csv (note year is appended to name passed to the function).
    Calculates percentages for the year 2019. All percentages shown are a percentage of the total import/export of the top 15 countries for the given year.
    """
    with open(filenamein+".csv") as fin:
        csvread = csv.reader(fin, delimiter=",")
        reader = list(csvread)
    top15exp = []
    top15imp = []
    for entry in reader:
        if entry[0]==str(year) and entry[2] in [country[1] for country in toptraders[0]]:
            top15exp.append(entry)
        if entry[0]==str(year) and entry[2] in [country[1] for country in toptraders[1]]:
            top15imp.append(entry)

    with open(exportoutput+str(year)+".csv", "w") as fout1:
        writer1 = csv.writer(fout1, lineterminator = "\n")
        writer1.writerow(["Country", "Jan%", "Feb%", "Mar%", "Apr%", "May%", "Jun%", "Jul%", "Aug%", "Sep%", "Oct%", "Nov%", "Dec%", r"Country % of Top 15 Total"])
        grandtotal = sum([float(entry[28]) for entry in top15exp])
        for entry in top15exp:
            total = float(entry[28])
            towrite = [entry[2]]
            for i in range (16, 29):
                towrite.append(str(round(float(entry[i])/grandtotal*100,3))+"%")
            writer1.writerow(towrite)
        subtotals = ["Total"]
        for month in range(16, 28):
            subtotals.append(str(round(sum([float(entry[month]) for entry in top15exp])/grandtotal*100,3))+"%")
        subtotals.append("100.00%")
        writer1.writerow(subtotals)

    with open(importoutput+str(year)+".csv", "w") as fout2:
        writer2 = csv.writer(fout2, lineterminator = "\n")
        writer2.writerow(["Country", "Jan%", "Feb%", "Mar%", "Apr%", "May%", "Jun%", "Jul%", "Aug%", "Sep%", "Oct%", "Nov%", "Dec%", r"Country % of Top 15 Total"])
        grandtotal = sum([float(entry[15]) for entry in top15imp])
        for entry in top15imp:
            total = float(entry[15])
            towrite = [entry[2]]
            for i in range (3, 16):
                towrite.append(str(round(float(entry[i])/grandtotal*100,3))+"%")
            writer2.writerow(towrite)
        subtotals = ["Total"]
        for month in range(3, 15):
            subtotals.append(str(round(sum([float(entry[month]) for entry in top15imp])/grandtotal*100,3))+"%")
        subtotals.append("100.00%")
        writer2.writerow(subtotals)



###test function call below:
#bonus("country", html_parser("foreign_trade"), "bonusexport", "bonusimport", 2020)
