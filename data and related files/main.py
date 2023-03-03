# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    with open('yelp_data.json',encoding="utf8") as data:
        print(type(data))
        data = json.load(data)
    fileToWrite = open("yelp_os_data.json", "w")
    document = []
    index = 0
    for each_data in data:
        fileToWrite.write(str({"index" : {"_index": "restaurants", "_id": str(index+1)}}))
        fileToWrite.write("\n")
        fileToWrite.write(str({"cuisine": each_data['cuisine'], "restaurantId": each_data['id']}))
        fileToWrite.write("\n")
        index = index+1

    #fileToWrite.write(str(document))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
