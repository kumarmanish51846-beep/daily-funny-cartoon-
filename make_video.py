import os, asyncio, subprocess, textwrap
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H = 720, 1280
OUT = "output"
os.makedirs(OUT, exist_ok=True)

# Daily rotation of original short comedy scripts. Each scene has two characters.
STORIES = [
    {"title":"होमवर्क का बहाना","pairs":[
        ("मम्मी: होमवर्क पूरा हुआ?","बच्चा: लगभग पूरा!"),
        ("मम्मी: कॉपी कहाँ है?","बच्चा: कॉपी तो स्कूल में है!"),
        ("मम्मी: तो किया क्या तुमने?","बच्चा: कॉपी को घर याद किया!"),
        ("मम्मी: अब कॉपी भी तुम्हें याद करेगी!","बच्चा: मम्मी, ये तो इमोशनल हो गया!")
    ]},
    {"title":"आलसी अलार्म","pairs":[
        ("अलार्म: उठ जाओ, सुबह हो गई!","लड़का: पाँच मिनट और!"),
        ("अलार्म: पाँच मिनट पहले भी यही कहा!","लड़का: तुम टाइम पर क्यों आते हो?"),
        ("अलार्म: मेरा काम जगाना है!","लड़का: मेरा काम सोना है!"),
        ("अलार्म: अब सच में उठ जाओ!","लड़का: आखिरकार समझदार मशीन!")
    ]},
    {"title":"परीक्षा का ज्ञान","pairs":[
        ("दोस्त: पेपर कैसा हुआ?","पप्पू: बहुत शानदार!"),
        ("दोस्त: सब सवाल आते थे?","पप्पू: नहीं, सवाल नए थे!"),
        ("दोस्त: फिर शानदार कैसे?","पप्पू: लिखावट तो शानदार थी!"),
        ("दोस्त: नंबर कितने आएँगे?","पप्पू: ये तो किस्मत बताएगी!")
    ]},
    {"title":"ऑनलाइन क्लास","pairs":[
        ("टीचर: कैमरा ऑन करो!","छात्र: नेटवर्क नहीं है!"),
        ("टीचर: आवाज़ तो आ रही है!","छात्र: वो पड़ोसी का नेटवर्क है!"),
        ("टीचर: जवाब कौन दे रहा है?","छात्र: मेरा टैलेंट, मैम!"),
        ("टीचर: अब होमवर्क भेजो!","छात्र: मैम, नेटवर्क फिर चला गया!")
    ]},
    {"title":"पापा का फोन","pairs":[
        ("पापा: फोन में क्या कर रहे हो?","बेटा: पढ़ाई का वीडियो देख रहा हूँ!"),
        ("पापा: क्या सीखा आज?","बेटा: बैटरी जल्दी खत्म होती है!"),
        ("पापा: किताब पढ़ो!","बेटा: उसमें बैटरी ही नहीं होती!"),
        ("पापा: अब किताब उठाओ!","बेटा: ये कैसा ट्विस्ट है!")
    ]},
    {"title":"चतुर दुकानदार","pairs":[
        ("ग्राहक: ये घड़ी सही टाइम बताती है?","दुकानदार: बिल्कुल!"),
        ("ग्राहक: अभी कितने बजे हैं?","दुकानदार: अपनी घड़ी में देखिए!"),
        ("ग्राहक: मेरी घड़ी बंद है!","दुकानदार: तभी तो नई बेच रहा हूँ!"),
        ("ग्राहक: बात तो सही है!","दुकानदार: धन्यवाद, अगला ग्राहक!")
    ]},
    {"title":"चाय का इंटरव्यू","pairs":[
        ("दोस्त: तुम्हारी सबसे बड़ी ताकत?","गोलू: चाय के साथ बिस्कुट!"),
        ("दोस्त: और कमजोरी?","गोलू: चाय के बिना सुबह!"),
        ("दोस्त: कोई खास हुनर?","गोलू: खाली कप पहचान लेता हूँ!"),
        ("दोस्त: नौकरी मिल गई!","गोलू: चाय कहाँ मिलेगी?")
    ]}
]

# Edge TTS voices: distinct Hindi voices for the two characters.
VOICE_A = "hi-IN-MadhurNeural"   # male
VOICE_B = "hi-IN-SwaraNeural"    # female
FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
def font(size, bold=True):
    idxs = [0,2] if bold else [1,3]
    for i in idxs:
        if os.path.exists(FONT_PATHS[i]):
            return ImageFont.truetype(FONT_PATHS[i], size)
    return ImageFont.load_default()

def centered(draw, text, y, fnt, fill, width=W):
    box = draw.textbbox((0,0), text, font=fnt)
    draw.text(((width-(box[2]-box[0]))//2, y), text, font=fnt, fill=fill)

def character(draw, cx, cy, shirt, mood):
    draw.ellipse((cx-65,cy-130,cx+65,cy+2), fill="#FFD6A5", outline="#333333", width=5)
    draw.arc((cx-72,cy-145,cx+72,cy-5),180,360,fill="#333333",width=13)
    draw.ellipse((cx-33,cy-82,cx-17,cy-64),fill="#222222")
    draw.ellipse((cx+17,cy-82,cx+33,cy-64),fill="#222222")
    if mood % 2 == 0:
        draw.arc((cx-28,cy-65,cx+28,cy-28),0,180,fill="#8B2F2F",width=5)
    else:
        draw.line((cx-22,cy-43,cx+22,cy-43),fill="#8B2F2F",width=5)
    draw.rounded_rectangle((cx-78,cy,cx+78,cy+180),radius=28,fill=shirt,outline="#333333",width=5)
    draw.line((cx-50,cy+175,cx-65,cy+245),fill="#333333",width=15)
    draw.line((cx+50,cy+175,cx+65,cy+245),fill="#333333",width=15)
    draw.line((cx-72,cy+35,cx-125,cy+105),fill="#333333",width=13)
    draw.line((cx+72,cy+35,cx+125,cy+105),fill="#333333",width=13)

def make_scene(title, pair, idx):
    bg = ["#FFF0C2","#DDF5FF","#E5FFD9","#FFE1EA"][idx % 4]
    img = Image.new("RGB",(W,H),bg); d = ImageDraw.Draw(img)
    d.ellipse((35,100,165,170),fill="white"); d.ellipse((95,75,220,170),fill="white")
    d.ellipse((500,135,630,200),fill="white")
    d.rectangle((0,900,W,H),fill="#B8E6A3")
    centered(d,"😂 FUNNY CARTOON SHORTS 😂",25,font(30), "#263238")
    centered(d,title,90,font(46), "#D84315")
    character(d,220,475,"#4D96FF",idx); character(d,510,475,"#FF6B6B",idx+1)
    d.rounded_rectangle((32,790,688,1070),radius=32,fill="white",outline="#333333",width=5)
    a,b = pair
    centered(d,a,825,font(29), "#222222")
    centered(d,b,920,font(29), "#222222")
    centered(d,"ऐसी और मज़ेदार वीडियो के लिए फॉलो करें!",1105,font(24), "#263238")
    centered(d,f"सीन {idx+1}/4",1190,font(22,False), "#444444")
    return img

def run(cmd):
    subprocess.run(cmd, check=True)

async def speak(text, voice, path):
    await edge_tts.Communicate(text, voice, rate="+8%").save(path)

def main():
    story = STORIES[(date.today().timetuple().tm_yday - 1) % len(STORIES)]
    # Each scene contains two separate voice clips, one per character.
    audio_files=[]
    for i,(a,b) in enumerate(story["pairs"]):
        for j,(line,voice) in enumerate([(a,VOICE_A),(b,VOICE_B)]):
            p=f"{OUT}/voice_{i}_{j}.mp3"
            asyncio.run(speak(line,voice,p)); audio_files.append(p)

    # Create scene images and a 60-second vertical video (4 scenes x 15 seconds).
    image_files=[]
    for i,pair in enumerate(story["pairs"]):
        p=f"{OUT}/scene_{i:02d}.png"
        make_scene(story["title"],pair,i).save(p); image_files.append(p)

    # Build 4 scenes at 15 seconds each; use a gentle fade between scenes.
    # Each dialogue audio clip is concatenated with a short pause to make timing comfortable.
    audio_list=f"{OUT}/audio_list.txt"
    with open(audio_list,"w",encoding="utf-8") as f:
        for p in audio_files:
            f.write(f"file '{os.path.abspath(p)}'\n")
            f.write("duration 0.15\n")
    # concat demuxer expects one last file without duration
    with open(audio_list,"a",encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(audio_files[-1])}'\n")
    dialogue=f"{OUT}/dialogue.mp3"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",audio_list,"-c:a","libmp3lame",dialogue])

    # Create each scene segment, then concatenate with fades.
    segments=[]
    for i,p in enumerate(image_files):
        seg=f"{OUT}/seg_{i}.mp4"; segments.append(seg)
        run(["ffmpeg","-y","-loop","1","-i",p,"-t","15",
             "-vf","fps=25,scale=720:1280,format=yuv420p",
             "-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",seg])
    concat=f"{OUT}/video_list.txt"
    with open(concat,"w",encoding="utf-8") as f:
        for p in segments: f.write(f"file '{os.path.abspath(p)}'\n")
    silent=f"{OUT}/silent.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c","copy",silent])
    final=f"{OUT}/funny_cartoon_short.mp4"
    # Keep video at ~60 seconds. Dialogue is padded with silence to fill the runtime.
    run(["ffmpeg","-y","-i",silent,"-i",dialogue,
         "-filter_complex","[1:a]apad=pad_dur=60,atrim=0:60[a]",
         "-map","0:v:0","-map","[a]","-t","60",
         "-c:v","copy","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",final])

    # Separate thumbnail image
    thumb=Image.new("RGB",(1280,720),"#FFE08A"); d=ImageDraw.Draw(thumb)
    d.ellipse((30,60,340,370),fill="#FFD6A5",outline="#333333",width=9)
    d.ellipse((220,170,530,480),fill="#FFD6A5",outline="#333333",width=9)
    d.ellipse((100,150,145,200),fill="#222222"); d.ellipse((230,150,275,200),fill="#222222")
    d.arc((120,190,260,310),0,180,fill="#8B2F2F",width=10)
    d.ellipse((300,260,345,305),fill="#222222"); d.ellipse((410,260,455,305),fill="#222222")
    d.arc((325,300,440,390),0,180,fill="#8B2F2F",width=10)
    d.rounded_rectangle((540,75,1235,560),radius=45,fill="white",outline="#D84315",width=12)
    centered(d,"😂 धांसू कॉमेडी 😂",155,font(62), "#D84315",width=1280)
    centered(d,story["title"],280,font(56), "#263238",width=1280)
    centered(d,"अंत तक देखना मत भूलना!",410,font(36), "#222222",width=1280)
    thumb.save(f"{OUT}/thumbnail.jpg",quality=92)

    # Title, description and hashtags as a text file ready to copy.
    title=f"{story['title']} 😂 | Funny Cartoon Shorts #Shorts"
    desc=(f"{story['title']} पर एक मज़ेदार हिंदी कार्टून कॉमेडी! 😂\n"
          "वीडियो पसंद आए तो Like, Share और Subscribe करें।\n\n"
          "#Shorts #FunnyCartoon #HindiComedy #CartoonShorts #Comedy")
    with open(f"{OUT}/youtube_title_description.txt","w",encoding="utf-8") as f:
        f.write("TITLE\n"+title+"\n\nDESCRIPTION\n"+desc+"\n")
    print("Created video, thumbnail, and YouTube title/description/hashtags.")

if __name__=="__main__":
    main()
