from bs4 import BeautifulSoup
import os
import matplotlib.pyplot as plt
import psutil

# Create the report
username = psutil.users()[0].name
filename = "C:/Users/" + username + "/battery-report.html"
command = "powercfg /batteryreport /output " + filename
os.system(command)

# Open the parser
with open(filename) as fp:
    soup = BeautifulSoup(fp, "html.parser")

# Create a list with all the elements
elements_list = soup.find_all()

# Create a list with all the elements with the tag <td> and the class "mw"
# The TDs within this class contain all the battery capacity values
td_mw_list = soup.find_all("td",class_="mw")

# Create a list with all the elements with the tag <td> and the class "dateTime"
td_date_list = soup.find_all("td",class_="dateTime")

i = 0
found = start_again = False

for element in elements_list:
    i+=1

    # If the current element has the tag <td>
    # And we still haven't found the text "Battery capacity history"
    # Remove the element from the list "td_mw_list"
    if element in td_mw_list and found==False:
        td_mw_list.remove(element)
    
    # Do the same for dates
    if element in td_date_list and (found==False or start_again==True):
        td_date_list.remove(element)

    # If we come across such text in the list of elements
    # Tell it by setting found = True
    # We choose i>50 (50 is a relatively big number, chosen for no particular reason)
    # Otherwise, the code would find the text too early
    if "Battery capacity history" in element.text and i>50:
        found = True

    if "Battery life estimates" in element.text and i>50:
        start_again = True
    
# The elements in the "td_mw_list" are in the format:
# <td class="mw">Text</td>
# We retrieve only the Text
i = 0
for td_element in td_mw_list:
    td_mw_list[i]= td_element.text
    i+=1

i = 0
for td_element in td_date_list:
    td_date_list[i]= td_element.text
    i+=1
    
# Cleans the Text so to only retrieve the Number
# By removing measurement units and spaces
i = 0
for td_element in td_mw_list:
    for character in td_element:
        if character==" " or character==".":
            td_element = td_element.replace(character,"")
    td_mw_list[i] = td_element.strip("mWh\n\n")
    i+=1

# Removes corresponding data from "design capacity"
# Because we are only interested in "full charge capacity"
design_capacity = td_mw_list[1]
while design_capacity in td_mw_list:
    td_mw_list.remove(design_capacity)

# PRINT DATA
# print("Dati: ", td_mw_list)

# Transofrm values in percentages
i = 0
for td_element in td_mw_list:
    td_mw_list[i] = int(td_element)/int(design_capacity)*100
    i+=1


# Clean the dates
i = 0
for x in td_date_list:
    cleaned_date = ""
    for character in td_date_list[i]:
        if character==" ":
            break
        cleaned_date += character
    td_date_list[i] = cleaned_date
    td_date_list[i] = "".join(td_date_list[i].split()) # rimuove gli spazi e i tab
    i+=1

# CHART
xaxis = []
for x in td_date_list:
    xaxis.append(x)

title = "Battery SoH History\n< Design Capacity = " + design_capacity + " mW >\n< Health since " + td_date_list[0] + " = " + str(round(td_mw_list[len(td_mw_list)-1],2)) + "% >"

plt.plot(xaxis,td_mw_list)
plt.title(title)
plt.xticks(rotation=75)
plt.grid()
plt.tight_layout()
plt.show()


