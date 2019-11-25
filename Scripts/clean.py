import csv
new_contacts = []  # This list is for all new contacts.
new_validated = [] # This list is for old contacts, who have been validated since the last export.
emails = []

# This is the value that represents if the contact has been previously validated.
NOT_VALIDATED = "0"



'''
    FUNCTION DEFINITIONS
'''

def sort_previous_contacts(file_name):
    previous = []
    indexed_previous_contacts = {}
    with open(file_name, "r") as csv_file:
        reader = csv.reader(csv_file)

        for contact in reader:
            if good_contact(contact):
                previous.append(contact)
            
    for contact in previous:
        email = contact[3]
        validation = contact[-2]
        indexed_previous_contacts[email] = validation

    return indexed_previous_contacts


def good_contact(row):
    '''
    This function returns true if the contact is:
     A. Not working for calibrate
     B. Not a duplicate
     C. Not a nonesense entry we've spotted
    '''
    if len(row) < 2:
        return False

    email = row[3]

    if email.endswith("@calibrate.co.nz"):
        return False
    # Nonesense email found data.
    if email.endswith("@hjkc.com"):
        return False
    if email in emails:
        return False

    return True

def newly_validated(email, validation):
    ''' 
    This only checks if the contact has been validated since the last export
    params:
        - email, string of contacts email
        - validation, string of validation condition. "0" for unvalidated, any other value for validated.
    '''
    return (validation is not NOT_VALIDATED and previous_contacts[email] is NOT_VALIDATED)


'''
    SCRIPT START 
'''

# Get Previous exports URL
previous_url = str(input("CSV Filename from the previous CLEANED export: \n > "))

print("Filing Previous Contacts...")
previous_contacts = sort_previous_contacts(previous_url) 
print("Previous contacts filing complete.")

# Get filename for the csv url.
latest_export_csv = str(input("Filename for the DIRTY export to be cleaned: \n > "))

print("Reading new export file...")
with open(latest_export_csv, "r") as read_file:
    reader = csv.reader(read_file)

    for contact in reader:
        email = contact[3] 
        validation = contact[-2]

        if good_contact(contact):

            # Check if the email was in the last export.
            if email in previous_contacts:

                # Compares the validation status of the current and previous contact.
                if newly_validated(email, validation):
                    new_validated.append(contact)

            else:
                new_contacts.append(contact)

            emails.append(email)
                
print("New contacts loaded.")

new_contact_file = str(input("Enter the filename for to write the NEW contacts to, which are CLEAN: \n > "))

print("Writing new and cleaned contacts to {0}...".format(new_contact_file))
with open(new_contact_file, "w") as write_file:
    writer = csv.writer(write_file)
    writer.writerows(new_contacts)

print("Finished writing new and clean contacts.")

newly_validated_contacts_file = str(input("Filename to write OLD CONTACTS which are NEWLY VALIDATED to: \n > "))
print("Writing newly validated contacts to {0}...".format(newly_validated_contacts_file))
with open(newly_validated_contacts_file, "w") as write_file:
    writer = csv.writer(write_file)
    writer.writerows(new_validated)

print("Finished writing old contacts, that have been validated since last export")

print("Total # of new contacts: {0}".format(len(new_contacts)))
print("Total # of newly validated contacts: {0}".format(len(new_validated)))
