import os
import re
import json
from copy import deepcopy

first=True

RESULT_TXT = 'result.txt'
STRUCTURE_NAME_TXT = 'structureList.txt'
SORTED_RESULT_TXT = 'sorted_result.txt'
DIRECTORY_SUFFIX_MAP = [
    {
        'directory': '/chests',
        'suffix': ''
    },
    {
        'directory': '/chests/village',
        'suffix': ''
    },
    {
        'directory': '/chests/trial_chambers',
        'suffix': ''
    },
    {
        'directory': '/dispensers/trial_chambers',
        'suffix': '_dispenser'
    },
    {
        'directory': '/pots/trial_chambers',
        'suffix': '_pot'
    },
    {
        'directory': '/spawners/trial_chamber',
        'suffix': '_spawner'
    },
    {
        'directory': '/spawners/ominous/trial_chamber',
        'suffix': '_ominous_spawner'
    },
]
DONT_MODIFIED_NAME_RULE = [
    {
        'directory': '/spawners/trial_chamber',
        'suffix': '_spawner',
        'struname': 'items_to_drop_when_ominous'
    }
]
DONT_GENERAT_DATA_RULE = [
    {
        'directory': '/chests/trial_chambers',
        'suffix': '',
        'struname': 'reward_ominous'
    },
    {
        'directory': '/chests/trial_chambers',
        'suffix': '',
        'struname': 'reward'
    }
]

def firstStructure(f):
    global first
    if first is False :
        f.writelines(',\n')
    else:
        first= False

def processStructureName(struname, directory, suffix):
    preProcessStructure = {
        'directory': directory,
        'suffix': suffix,
        'struname': struname
    }
    if suffix == '' or preProcessStructure in DONT_MODIFIED_NAME_RULE:
        return struname
    return struname + suffix

def dontGenerateLootChestResult(struname, directory, suffix):
    preProcessStructure = {
        'directory': directory,
        'suffix': suffix,
        'struname': struname
    }
    return preProcessStructure in DONT_GENERAT_DATA_RULE

def generateLootChestResult(directory, suffix, f, doc):
    filedir = os.getcwd()+ directory
    filenames = os.listdir(filedir)
    for filename in filenames:
        if re.search('json', filename):
            filepath = filedir+'/'+filename
            struname = re.sub(r'\..*$', "", filename)
            struname = processStructureName(struname, directory, suffix)
            if dontGenerateLootChestResult(struname, directory, suffix):
                continue
            if generateSpecialLootChestResult(struname, directory, suffix, f, doc, filepath):
                continue
            doc.writelines(struname+'\n')
            firstStructure(f)
            f.writelines('"'+struname+'": ')
            for line in open(filepath):
                f.writelines(line)

def generateSpecialLootChestResult(struname, directory, suffix, f, doc, filepath):
    if directory == '/chests' and suffix == '' and struname == 'abandoned_mineshaft':
        ABANDONED_MINESHAFT_NOT_IN_SULFUR_CAVE = 'abandoned_mineshaft'
        ABANDONED_MINESHAFT_IN_SULFUR_CAVE = 'abandoned_mineshaft_in_sulfur_cave'
        with open(filepath, 'r', encoding='utf-8') as rawDataFile:
            rawData = json.load(rawDataFile)
        abandonedMineshaftNotInSulfurCaveData = deepcopy(rawData)
        abandonedMineshaftInSulfurCaveData = deepcopy(rawData)
        for pool in abandonedMineshaftNotInSulfurCaveData["pools"]:
            pool["entries"] = [entry for entry in pool["entries"] if "conditions" not in entry]
        for pool in abandonedMineshaftInSulfurCaveData["pools"]:
            for entry in pool["entries"]:
                entry.pop("conditions", None)
        doc.writelines(ABANDONED_MINESHAFT_NOT_IN_SULFUR_CAVE + '\n' + ABANDONED_MINESHAFT_IN_SULFUR_CAVE + '\n')
        firstStructure(f)
        f.write('"' + ABANDONED_MINESHAFT_NOT_IN_SULFUR_CAVE + '": ')
        json.dump(abandonedMineshaftNotInSulfurCaveData, f, ensure_ascii=False, indent=2)
        f.write(',\n')
        f.write('"' + ABANDONED_MINESHAFT_IN_SULFUR_CAVE +'": ')
        json.dump(abandonedMineshaftInSulfurCaveData, f, ensure_ascii=False, indent=2)
        return True
    return False

def sortLootChestResult(inputFile, outputFile):
    with open(inputFile, 'r', encoding='utf-8') as f:
        data = json.load(f)
        sortedData = dict(sorted(data.items()))
    with open(outputFile, 'w', encoding='utf-8') as f:
        json.dump(sortedData, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    f=open(RESULT_TXT,'w')
    doc=open(STRUCTURE_NAME_TXT,'w')
    f.writelines('{\n')
    for value in DIRECTORY_SUFFIX_MAP:
        generateLootChestResult(value['directory'], value['suffix'], f, doc)
    f.writelines('\n}')
    f.close()
    sortLootChestResult(RESULT_TXT, SORTED_RESULT_TXT)