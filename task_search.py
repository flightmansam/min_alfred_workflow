from nis import match
import sys
from pathlib import Path
import json
from thefuzz import process


def main():
    """Configurations
    
    1. Show available tasks to open min to: task_search.py 
    2. Search available tasks to open min to: task_search.py ",<taskQuery>"
    3. Show available tasks to open min with a search query: task_search.py "<searchQuery>"
    4. Search available tasks to open min with a search query: task_search.py  "<searchQuery>,<taskQuery>"
    
    """

    alfred = None
    
    args = [a.strip() for a in sys.argv[1].split(',')]
        
    if len(args) == 1:
        tasks = sort_tasks(getTasks())
        if args[0] == "":
            #Config 1
            alfred = alfred_items(tasks)
        else:    
            #Config 3
            alfred = alfred_items(tasks, query=args[0])
    
    elif len(args) == 2:
        tasks = getTasks(search=args[1])
        if args[0] == "":
            #Config 2.
            alfred = alfred_items(tasks)
        else:
            #Config 4.
            alfred = alfred_items(tasks, query=args[0])

    alfred_json = json.dumps({
        "items": alfred
    }, indent=2)

    return alfred_json

def sort_tasks(tasks):
    for i, t in enumerate(tasks):
        latest_time= 0
        for tab in t["tabs"]:
            if tab["lastActivity"] > latest_time:
                latest_time = tab["lastActivity"]
        tasks[i]["lastActivity"] = latest_time
    
    return sorted(tasks, key= lambda x: x["lastActivity"], reverse=True)  

def alfred_items(tasks, query = None):

    formattedTasks = []

    if query:
        for t in tasks:
            try:
                key = t['id']
            except KeyError:
                key = t['name']
            result = {
                "title": t["name"],
                "subtitle": f"Search for '{query}' in {t['name']}",
                "arg": f"{key},{query}",
                "icon": {
                    "path": "./icon.png"
                }
            }
            formattedTasks.append(result)
    else:
        for t in tasks:
            try:
                key = t['id']
            except KeyError:
                key = t['name']
            result = {
                "title": t["name"],
                "subtitle": f"Open {t['name']} in min",
                "arg": f"{key}",
                "icon": {
                    "path": "./icon.png"
                }
            }
            formattedTasks.append(result)

    return formattedTasks

def getTasks(search: str = None):
    taskFile = Path("/Users/samuel/Library/Application Support/Min/sessionRestore.json")
    if taskFile.exists():
        with open(taskFile, 'r') as fh:
            taskJSON = json.load(fh)
        
        tasks = taskJSON['state']['tasks']

        for i, t in enumerate(tasks):
            if t['name'] is None:
                t['name'] = f"Task {i+1}"
        
        if search:
            
            tasks = {t['name']:t for t in tasks}

            matches = process.extractBests(query=search, choices=tasks.keys())
            
            matches = list(filter(lambda x: x[1] > 60, matches))

            if len(matches) > 0:    
                keys, scores = list(zip(*matches))
                tasks = [tasks[t] for t in keys]
            elif len(search) > 0:
                tasks = [{'name':search}]

        return tasks

    #else
    return []
    
if __name__ == '__main__':
    sys.stdout.write(main()) 