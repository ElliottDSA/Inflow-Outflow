# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
import pandas as pd
import datetime as dt




#def is_active(short_frame):
    #run the 90 day filter for a particular client.
    #return active_frame


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #Read PDR in
    my_contacts = pd.read_csv("C:/Users/elliott.lapinel/Downloads/active_inactive_two.csv",
                              na_values=['nan'], encoding = 'unicode_escape')

    #Generate list of last days of the mont
    last_day_of_month = pd.Series(pd.date_range(start='2017-01', freq='M', periods=200))
    #Format Dates - may need to change 'mix' to avoid bug?
    my_contacts['Information Date'] = pd.to_datetime(my_contacts['Information Date'], format="mixed")
    my_contacts['Entry Date'] = pd.to_datetime(my_contacts['Entry Date'], format="mixed")
    my_contacts['Exit Date'] = pd.to_datetime(my_contacts['Exit Date'], format="mixed")
    my_contacts["HMID"] =pd.to_datetime(my_contacts["HMID"], format="mixed")

    #For some reason, get the most recent date for programs - ignoring information date
    most_recent_entry_exit = my_contacts.copy()
    entry_exit_cols = my_contacts[["Entry Date", "Exit Date"]]
    most_recent_entry_exit["recent_date"] = entry_exit_cols.max(1)
    most_recent_entry_exit = most_recent_entry_exit.sort_values(by=['recent_date'], ascending=False)
    most_recent_entry_exit = most_recent_entry_exit.drop_duplicates(subset=["Client Id"])
    most_recent_entry_exit.rename({"HMID": "Housed_Maybe"})


    #Set exits from coordinated entry to null - that doesn't count as a 'contact'
    my_contacts.loc[my_contacts["Provider"] == "Marion and Polk Coordinated Assessment_Homeless (5791)(5791)", "Exit Date"] = np.nan
    #I think I was just checking this
    my_nulls = my_contacts[my_contacts["Provider"] == "Marion and Polk Coordinated Assessment_Homeless (5791)(5791)"]
    #Get a subset of the PDR, that's just the columns I'm interested in.

    #Should I use HMID as a way of determining latest date for each row?
    cols = my_contacts[['Information Date', 'Entry Date', 'Exit Date']]
    #Create 'latest date' that is the latest date for each row.
    my_contacts['latest_date'] = cols.max(1)

    #adding length of time homeless
    my_contacts["length_stay"] = my_contacts["Exit Date"] - my_contacts["Entry Date"]
    my_contacts["cumulative_lot"] = my_contacts.groupby("Client Id")["length_stay"].cumsum()


    bfz_frame = my_contacts.sort_values(by=['Entry Date'], ascending=True)
    bfz_frame = bfz_frame.drop_duplicates(subset = ["Client Id"])
    bfz_frame["bfz_status"] = "first_identified"
    bfz_frame["bfz_date"] = bfz_frame["Entry Date"]
    #bfz_frame = my_contacts.copy()

    for month in last_day_of_month:
        #bug in chopping off latest date past month
        short_pdr = my_contacts.copy()
        #Probably going to filter based on Entry and HMID
        entry_filter = short_pdr["Entry Date"] > month
        exit_filter = short_pdr["Exit Date"] > month
        information_filter = short_pdr["Information Date"] > month
        #
        short_pdr.loc[entry_filter, "Entry Date"] = np.nan
        short_pdr.loc[exit_filter, "Exit Date"] = np.nan
        short_pdr.loc[information_filter, "Information Date"] = np.nan
        cols = short_pdr[['Information Date', 'Entry Date', 'Exit Date']]
        short_pdr['latest_date'] = cols.max(1)

        #redundant?
        short_pdr = short_pdr[short_pdr['latest_date'] <= month]
        #set date to null if it is larger than month
        short_pdr = short_pdr[short_pdr['latest_date'] >= (month - pd.DateOffset(months=3))]
        short_pdr = short_pdr.sort_values(by=["latest_date"], ascending = False)
        short_pdr = short_pdr.drop_duplicates(subset = ["Client Id"])

        #Add housing move in date code ******************
        housed_pdr = short_pdr[pd.notna(short_pdr['HMID'])]
        #End housing move in date code *************************

        #Get most recent row of bfz_frame!
        bfz_list = bfz_frame.sort_values(by=["bfz_date"], ascending = False)
        bfz_list = bfz_list.drop_duplicates(subset = ["Client Id"])
        #Give me list of 'active'/inflow clients
        active_bfz = bfz_list[(bfz_list["bfz_status"] == "first_identified") | (bfz_list["bfz_status"] == "returned")]
        active_bfz = active_bfz[active_bfz["bfz_date"] <= month]
        inactive_bfz = bfz_list[bfz_list["bfz_status"] == "inactive"]
        inactive_bfz = inactive_bfz[inactive_bfz["bfz_date"] <= month]
        inactive = active_bfz[~active_bfz["Client Id"].isin(short_pdr["Client Id"])]
        active = inactive_bfz[inactive_bfz["Client Id"].isin(short_pdr["Client Id"])]
        #print(np.shape(inactive))
        inactive.loc[:, "bfz_status"] = "inactive"
        active.loc[:, "bfz_status"] = "returned"
        inactive.loc[:, "bfz_date"] = month
        active.loc[:, "bfz_date"] = month
        bfz_frame = pd.concat([bfz_frame, inactive, active])
        #print(bfz_frame)
        #print(first_identified["Client First Name"])
        #active_frame()



    #print the shebang
    bfz_frame.to_csv("C:/Users/elliott.lapinel/Downloads/active_inactive.csv")
    #sort my contacts by the latest date
    my_contacts = my_contacts.sort_values(by=['latest_date'], ascending=False)


    #



    #


    #drop duplicates - I only have the most recent date
    my_contacts = my_contacts.drop_duplicates(subset=["Client Id"])
    #grab the services
    my_services = pd.read_csv("C:/Users/elliott.lapinel/Downloads/service_ninety_April.csv", parse_dates=True,
                              na_values=['nan'])
    #format the need date column as a date
    my_services['Need Date'] = pd.to_datetime(my_services['Need Date'])
    #pull out the client id. Unhelpfully call it 'name'
    my_services["Name"] = my_services["Name"].str.extract('(\d+)')
    #sort by latest date
    my_services = my_services.sort_values(by=['Need Date'], ascending=False)
    #drop the duplicates
    my_services = my_services.drop_duplicates(subset=["Name"])



    #convert the client id to numeric type
    my_services["Name"] = pd.to_numeric(my_services["Name"])
    #I might not want to merge - might be better to keep these as separate rows.
    will_work = my_contacts.set_index("Client Id").join(my_services.set_index("Name"), how="right",
                                                        rsuffix="_right", lsuffix="_left")


    #Get latest date of original PDR and services
    date_columns = will_work[["latest_date","Need Date"]]
    will_work["ultimate_date"] = date_columns.max(1)
    #filter out clients whose contact is too old.



    active_clients = will_work[will_work["ultimate_date"] > pd.to_datetime("2022-4-24")]

    #Find everyone who has ever had an entry into coordinated entry
    should_be_in = pd.read_csv("C:/Users/elliott.lapinel/Downloads/should_be_in.csv", parse_dates=True,
                              na_values=['nan'], encoding='unicode_escape')


    #Merge with clients who are active in the system
    active_CE = should_be_in.set_index("Client ID").join(active_clients,how="inner")

    #Find everyone who is recently in coordinated entry
    are_in = pd.read_csv("C:/Users/elliott.lapinel/Downloads/are_in.csv", parse_dates=True,
                               na_values=['nan'], encoding='unicode_escape')



    active_CE["Client Id"] = active_CE.index
    in_list = are_in["Client ID"]
    need_in = active_CE.loc[~active_CE["Client Id"].isin(in_list)]

    jimmy_list = need_in.join(most_recent_entry_exit.set_index("Client Id"),how="left", lsuffix="lefty", rsuffix ="righty")

    #jimmy_list.to_csv("C:/Users/elliott.lapinel/Downloads/jimmy_list.csv")
