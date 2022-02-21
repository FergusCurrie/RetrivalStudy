import osd
from datetime import date
import json
import sys
import subprocess


"""
This is going to control my active recal for uni, i'll connect to git to backup. 

3 Focuses for long-term learning : 
    - Active Recal 
    - Interleaving 
    - Spaced repetition 
    
Import to chunk all information well 
    
to add : 
    - summary statistics 
    - itnerleaving , so a measure for distance 
    - tree visualisation 
"""

custom_date = "None"

def save_node(dict,path):
    with open(path + "/meta.json", 'w+') as file:
        file.write(json.dumps(dict))

def todays_date():
    # yyyy-mm-dd
    if custom_date == "None":
        return date.today()
    else:
        z = custom_date.split("-")
        return date(int(z[0]), int(z[1]), int(z[2]))



def process_all_notes(func,dir="./Active_Recal_Notes",depth=0):
    """
    Applies a function to every file recursively. 

    """
    r = [] # return

    # Make the recusrive call on other directorys
    for x in os.listdir(dir):
        if os.path.isdir(dir+"/"+x):
            r = r + process_all_notes(func,dir=(dir+"/"+x),depth=depth+1)

    # Process a leaf
    if "LEAF" in dir:
        # Check if meta exists
        meta_exists = True
        try:
            open(dir + "/meta.json")
        except:
            meta_exists = False

        # If meta exists, process by reading it into a dict, then applying the function
        if meta_exists:
            with open(dir+"/meta.json") as file:
                data = json.load(file)
                # apply function
                r = r + func(data)

        # If meta doesn't exist, create
        if not meta_exists:
            new_meta = {
                "name": dir.split("/")[len(dir.split("/")) - 1].replace("LEAF_", ""),
                "path": dir,
                "rep_num": 0,
                "rep_dates": [str(todays_date())],
                "ef": 2.5,
                "interval": 0
            }
            save_node(new_meta,dir) # uses json to dump into meta.json 

    # Return
    return r

# APPLICATION METHODS

def empty_func(dict):
    return []

def get_to_study(dict):
    z = dict["rep_dates"][len(dict["rep_dates"])-1].split("-")
    most_recent_study = date(int(z[0]),int(z[1]),int(z[2]))
    interval = dict["interval"]
    if (todays_date() - most_recent_study).days >= interval:
        return [dict]
    return []


# STUDYING METHODS

def sm2(dict,q):
    """
    updates a card that has been read

    https://en.wikipedia.org/wiki/SuperMemo
    takes dict for card, returns updated dict for card

    """
    n = int(dict['rep_num'])
    i = float(dict['interval'])
    ef = float(dict['ef']) # easiness factor

    # Correct
    if q >= 3:
        if n == 0:
            i = 1
        elif n == 1:
            i = 6
        else:
            i = i * ef
        ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)) # dunno this is straight from wiki
        if ef < 1.3:
            ef = 1.3
        n = n + 1
    else:
        # Incorrect
        n = 0
        i = 1

    # Update and return
    dict['rep_num'] = n
    dict['interval'] = i
    dict['ef'] = ef
    dict['rep_dates'].append(str(todays_date()))

    return dict


def study_loop(to_study):
    """
    Loop to study. Takes list of cards, iteraviely displays them, allows scoring, and updates the meta info

    Args:
        to_study : list of cards 
    Returns nothing
    """
    studied = False
    for card in to_study:
        studied = True
        #subprocess.Popen([open(card['path']+card['name']+'.pdf'])],shell=True)
        print()
        print("Card to study : "+card['name'])

        # Get result
        score = ""
        #input("PRESS ANYTHING WHEN DONE")
        p =  card['path']+'/'+card['name']+'.pdf'
        input("PRESS ENTER TO CONTINUE")
        subprocess.call(('open',p))
        print(p)
        while score == "":
            score = input("""
            0: "Total blackout", complete failure to recall the information.
            1: Incorrect response, but upon seeing the correct answer it felt familiar.
            2: Incorrect response, but upon seeing the correct answer it seemed easy to remember.
            3: Correct response, but required significant difficulty to recall.
            4: Correct response, after some hesitation.
            5: Correct response with perfect recall.
            //
            How did it go: """)
            if not score in ["0","1","2","3","4","5","stop"] :
                print("Error, try again")
                score = ""

        # If stop
        if score == "stop":
            break

        # Update card
        updated_card = sm2(card,int(score))
        save_node(updated_card,card['path']) # json dump updated meta 
    if not studied:
        print("Nothing to study!")







if __name__ == "__main__":
    process_all_notes(func=empty_func)
    if len(sys.argv) != 2:
        print("Incorrect arguments supplied")
    else:
        arg = sys.argv[1]
        if arg == "--study":
            to_study = process_all_notes(func=get_to_study) # pass the get to study func
            study_loop(to_study)
        if arg == "--test":
            # For testing, allows a custom date to be used
            custom_date="2021-05-27"
            to_study = process_all_notes(func=get_to_study)
            study_loop(to_study)




