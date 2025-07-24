# ROtools 
Version 2.0

Unblacklister and unique ID changer 

Setup: 
1. In ROtools folder create a folder and rename it to Maps.
   Only works on .rbxlx files.
   

How to use: 
------------------------------------
**Modes:** 
It comes with 4 modes [**add**|**regenerate**|**unblacklist**|**full**]
**add:** Adds new unique ID strings to all game assets. It won't add strings to the following parents:
   "PackageLink", "BinaryString", "FloatCurve", "NumberSequence",
    "ColorSequence", "SharedTable", "SoundService", "Chat", "TextChatService",
    "VoiceChatService", "LocalizationService", "TestService", "VRService",
    "Players", "Lighting", "MaterialService"

**regenerate:** Updates all existing IDs and adds new ones if needed

**unblacklist:** Unblacklists the file
**full:** Everything above is applied for harder detections

python toolkit.py --mode MODE_SETTING_HERE
example: **python toolkit.py --mode full**



Changelog:
------------------------------------
None

