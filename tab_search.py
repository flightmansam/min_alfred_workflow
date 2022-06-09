from nis import match
import sys
from pathlib import Path
import json
from thefuzz import process


def main():
    # Main    s


    args = sys.argv[1].split(',') 

    if len(args) == 1:
        tabs = getTabs(search=args[0])
    elif len(args) == 2:
        tabs = getTabs(search=args[1])

    alfred_json = json.dumps({
        "items": get_alfred_items(tabs, query=args[0])
    }, indent=2)

    return alfred_json

def sort_tasks(tasks):
    for i, t in enumerate(tasks):
        latest_time = 0
        for tab in t["tabs"]:
            if tab["lastActivity"] > latest_time:
                latest_time = tab["lastActivity"]
        tasks[i]["lastActivity"] = latest_time
    
    return sorted(tasks, key= lambda x: x["lastActivity"], reverse=True)
        
def get_alfred_items(tabs, query):

    formattedTabs = []

    for t in tabs:
        result = {
            "title": t["title"],
            "arg": f"",
            "icon": {
                "path": "./icon.png"
             }
        }
        formattedTabs.append(result)

    return formattedTabs

def getTabs(search):
    taskFile = Path("/Users/samuel/Library/Application Support/Min/sessionRestore.json")
    if taskFile.exists():
        with open(taskFile, 'r') as fh:
            taskJSON = json.load(fh)
        
        tasks = taskJSON['state']['tasks']
        
        tabs = []
        for i, t in enumerate(tasks):
            if t['name'] is None:
                t['name'] = f"Task {i+1}"
            tabs += t["tabs"]
            
        # tasks = {t['name']:t for t in tasks}
        # URLmatches = list(filter(lambda x: x[1] > 30, process.extractBests(query=search, choices=[t['url'] for t in tabs])))
        titlematches = list(filter(lambda x: x[1] > 20, process.extractBests(query=search, choices=[t['title'] for t in tabs], limit=100)))
        
        if len(titlematches) > 0:    
            keys, scores = list(zip(*titlematches))
            tabs = list(filter(lambda x: x['title'] in keys, tabs))
            print(keys, scores)
        else:
            tabs = []

        return tabs

    #else
    return []
    



if __name__ == '__main__':
    sys.stdout.write(main()) 