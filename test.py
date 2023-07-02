import whisper_timestamped as whisper
import ssl
import json
import re
from fuzzywuzzy import fuzz as f
from langdetect import detect, DetectorFactory
import random
from utils import lyrics_tsv, app, s3_client, Bucket
from pydub import AudioSegment
import glob, os
from graphql import get_table_from_graphql, create_entry, update_entry


@app.get("/url_download")
def get_url(music_id):
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': Bucket, 'Key': f'{music_id}.mp3'},
        ExpiresIn=600)
    return url


@app.get("/nn_timecode")
def nn_timecode(music_id):
    DetectorFactory.seed = 0
    lang = detect(lyrics_tsv[f'{music_id}'])

    ssl._create_default_https_context = ssl._create_unverified_context
    s3_client.download_file(Bucket, f'{music_id}.mp3', f'{music_id}.mp3')
    with open(f'{music_id}.txt', "w") as song_text:
        song_text.write(lyrics_tsv[music_id])

    audio = whisper.load_audio(f'{music_id}.mp3')

    # подгрузка модели
    model = whisper.load_model("base.en" if lang == 'en' else "base", device="cpu")

    text_music = open(f'{music_id}.txt', 'r').read()
    array_line_music = re.sub(r'[^\w\s]', '', text_music.replace("\\n", "\n").replace("\n\n", "\n")).split("\n")

    # распознание слов
    result = whisper.transcribe(model, audio, language=lang, condition_on_previous_text=False,
                                initial_prompt=array_line_music[0], temperature=(0.0, 0.2, 0.4, 0.6))["segments"]

    # вытаскиваем слова из ответа нейронки
    word_list = []
    for segment in result:
        for word in segment["words"]:
            word_list.append(word)
    # Записываем результат работы нейронки для лога
    open(f'{music_id}_logs.json', 'w').write(json.dumps(word_list, ensure_ascii=False, indent=4))

    # читаем оригинальный текс, удаляем знаки препинания и формируем лист из строк песни
    # array_line_music = str(lyrics_tsv[f'{music_id}']).replace("\\n", "\n").replace("\n\n", "\n").split("\n")
    # array_line_music = re.sub(r'[^\w\s]', '', text_music).split("\n")
    '''text_music = lyrics_tsv[f'{music_id}']
    array_line_music = re.sub(r'[^\w\s]', '', text_music.replace("\n\n", "\n").replace("\\n", "\n")).split("\n")'''

    '''text_music = open(f'{music_id}.txt', 'r').read()
    array_line_music = re.sub(r'[^\w\s]', '', text_music.replace("\n\n", "\n")).split("\n")'''
    main_list = []
    obj = word_list
    for i in obj:
        i["text"] = re.sub(r'[^\w\s]', '', i["text"])

    old_number_word = 0
    e = 0
    for line in array_line_music:
        test_array = []

        for i in range(old_number_word, min(old_number_word + 20, len(obj))):
            a = {"start_word": old_number_word, "end_word": i - 1, "start_time": obj[old_number_word]["start"],
                 "end_time": obj[i - 1]["end"],
                 "ratio": f.ratio(" ".join([x["text"] for x in obj[old_number_word:i]]), line),
                 "text_test": " ".join([x["text"] for x in obj[old_number_word:i]])}
            test_array.append(a)

        max_x = max(test_array, key=lambda x: x["ratio"])
        main_list.append({"number_line": e, "text_line": line, "start_word": max_x["start_word"],
                          "end_word": max_x["end_word"], "start_time": max_x["start_time"],
                          "end_time": max_x["end_time"],
                          "ratio": max_x["ratio"], "text_test": max_x["text_test"]})
        old_number_word = max_x["end_word"] + 1
        e += 1
    list_ratio = []
    for el in main_list:
        list_ratio.append(el["ratio"])
    min_r = min(list_ratio)
    avg_r = sum(list_ratio) / len(list_ratio)
    file = open(f'{music_id}.json', 'w')
    file.write(json.dumps(main_list, ensure_ascii=False, indent=4))
    final_info = {
        "idS3": music_id,
        "songLyrics": main_list,
        "meta": {},
        "published": 'true' if (list_ratio.count(0) <= 2 and avg_r >= 50) else 'false',
        "Author": 'Untitled',
        "Title": "Untitled",
        "minRatio": min_r,
        "averageRatio": avg_r,
        "language": lang}

    if get_table_from_graphql('Music', music_id):
        create_entry('Music', final_info)
    else:
        personal_id = get_table_from_graphql('Music', music_id)[0]['data']['id']
        update_entry('Music', personal_id, final_info)
    for files in glob.glob(f"{music_id}*"):
        os.remove(files)
    return final_info


def nn_test(music_id):
    DetectorFactory.seed = 0
    lang = detect(lyrics_tsv[f'{music_id}'])

    ssl._create_default_https_context = ssl._create_unverified_context
    # s3_client.download_file(Bucket, f'{music_id}.mp3', f'{music_id}.mp3')

    audio = whisper.load_audio(f'for_test/{music_id}.mp3')

    # подгрузка модели
    model = whisper.load_model("base", device="cpu")

    # распознание слов
    result = whisper.transcribe(model, audio, language=lang, condition_on_previous_text=False)["segments"]

    # вытаскиваем слова из ответа нейронки
    word_list = []
    for segment in result:
        for word in segment["words"]:
            word_list.append(word)
    # Записываем результат работы нейронки для лога
    open(f'for_test/{music_id}_logs.json', 'w').write(json.dumps(word_list, ensure_ascii=False, indent=4))

    # читаем оригинальный текс, удаляем знаки препинания и формируем лист из строк песни
    # array_line_music = str(lyrics_tsv[f'{music_id}']).replace("\\n", "\n").replace("\n\n", "\n").split("\n")
    # array_line_music = re.sub(r'[^\w\s]', '', text_music).split("\n")
    text_music = open(f'for_test/{music_id}.txt', 'r').read()
    array_line_music = re.sub(r'[^\w\s]', '', text_music.replace("\n\n", "\n").replace("\\n", "\n")).split("\n")

    main_list = []
    obj = word_list
    for i in obj:
        i["text"] = re.sub(r'[^\w\s]', '', i["text"])

    old_number_word = 0
    e = 0
    for line in array_line_music:
        test_array = []

        for i in range(old_number_word, min(old_number_word + 20, len(obj))):
            a = {"start_word": old_number_word, "end_word": i - 1, "start_time": obj[old_number_word]["start"],
                 "end_time": obj[i - 1]["end"],
                 "ratio": f.ratio(" ".join([x["text"] for x in obj[old_number_word:i]]), line),
                 "text_test": " ".join([x["text"] for x in obj[old_number_word:i]])}
            test_array.append(a)

        max_x = max(test_array, key=lambda x: x["ratio"])
        main_list.append({"number_line": e, "text_line": line, "start_word": max_x["start_word"],
                          "end_word": max_x["end_word"], "start_time": max_x["start_time"],
                          "end_time": max_x["end_time"],
                          "ratio": max_x["ratio"], "text_test": max_x["text_test"]})
        old_number_word = max_x["end_word"] + 1
        e += 1
    list_ratio = []
    for el in main_list:
        list_ratio.append(el["ratio"])
    min_r = min(list_ratio)
    avg_r = sum(list_ratio) / len(list_ratio)
    file = open(f'for_test/{music_id}.json', 'w')
    file.write(json.dumps(main_list, ensure_ascii=False, indent=4))
    final_info = {"idS3": music_id, "songLyrics": main_list, "meta": " ", "author": "Untitled", "title": "Untitled",
                  "minRatio": min_r, "averageRatio": avg_r}
    return final_info


@app.get("/random_song")
def random_songs(num: int):
    list_id = []
    for i in range(num):
        random_id = random.choice(list(lyrics_tsv.keys()))
        with open(f'for_test/{random_id}.txt', "w") as song_text:
            song_text.write(lyrics_tsv[random_id])
        s3_client.download_file(Bucket, f'{random_id}.mp3', f'for_test/{random_id}.mp3')
        song_json = open(f'for_test/{random_id}.json', "w")
        logs_json = open(f'for_test/{random_id}_logs.json', "w")
        nn_test(random_id)
        list_id.append(nn_test(random_id))
    return list_id



@app.get("/piece_test")
def piece_test(music_id):
    DetectorFactory.seed = 0
    lang = detect(lyrics_tsv[f'{music_id}'])
    # lang = 'ru'

    ssl._create_default_https_context = ssl._create_unverified_context
    s3_client.download_file(Bucket, f'{music_id}.mp3', f'temp/{music_id}.mp3')

    with open(f'temp/{music_id}.txt', "w") as song_text:
        song_text.write(lyrics_tsv[music_id])
    song_json = open(f'temp/{music_id}.json', "w")
    logs_json = open(f'temp/{music_id}_logs.json', "w")

    song = AudioSegment.from_mp3(f'temp/{music_id}.mp3')
    # song = AudioSegment.from_mp3(f'noise/Song.mp3')
    num = 0
    while len(song) >= 25000:
        part_song = song[:25000]
        song = song[25000:]
        part_song.export(f"temp/{music_id}_{num}.mp3", format="mp3")
        # part_song.export(f'noise/Song_{num}.mp3', format="mp3")
        num += 1
    song.export(f'temp/{music_id}_{num}.mp3', format="mp3")

    # подгрузка модели
    model = whisper.load_model("base", device="cpu")
    word_list = []
    for i in range(num + 1):
        audio = whisper.load_audio(f'temp/{music_id}_{i}.mp3')
        # audio = whisper.load_audio(f'noise/Song_{i}.mp3')

        # распознание слов
        result = whisper.transcribe(model, audio, language=lang, condition_on_previous_text=False)["segments"]

        # вытаскиваем слова из ответа нейронки
        for segment in result:
            for word in segment["words"]:
                word['start'] = word['start'] + i * 25
                word['end'] = word['end'] + i * 25
                word_list.append(word)
        # Записываем результат работы нейронки для лога
    open(f'temp/{music_id}_logs.json', 'a').write(json.dumps(word_list, ensure_ascii=False, indent=4))
    # open(f'noise/out.json', 'w').write(json.dumps(word_list, ensure_ascii=False, indent=4))

    # читаем оригинальный текс, удаляем знаки препинания и формируем лист из строк песни
    # array_line_music = str(lyrics_tsv[f'{music_id}']).replace("\\n", "\n").replace("\n\n", "\n").split("\n")
    # array_line_music = re.sub(r'[^\w\s]', '', text_music).split("\n")
    text_music = open(f'temp/{music_id}.txt', 'r').read()
    # text_music = open(f'noise/Noize MC - Устрой Destroy.txt', 'r').read()
    array_line_music = re.sub(r'[^\w\s]', '', text_music.replace("\n\n", "\n").replace("\\n", "\n")).split("\n")

    main_list = []
    obj = word_list
    for i in obj:
        i["text"] = re.sub(r'[^\w\s]', '', i["text"])

    old_number_word = 0
    e = 0
    for line in array_line_music:
        test_array = []

        for i in range(old_number_word, min(old_number_word + 20, len(obj))):
            a = {"start_word": old_number_word, "end_word": i - 1, "start_time": obj[old_number_word]["start"],
                 "end_time": obj[i - 1]["end"],
                 "ratio": f.ratio(" ".join([x["text"] for x in obj[old_number_word:i]]), line),
                 "text_test": " ".join([x["text"] for x in obj[old_number_word:i]])}
            test_array.append(a)

        max_x = max(test_array, key=lambda x: x["ratio"])
        main_list.append({"number_line": e, "text_line": line, "start_word": max_x["start_word"],
                          "end_word": max_x["end_word"], "start_time": max_x["start_time"],
                          "end_time": max_x["end_time"],
                          "ratio": max_x["ratio"], "text_test": max_x["text_test"]})
        old_number_word = max_x["end_word"] + 1
        e += 1
    list_ratio = []
    for el in main_list:
        list_ratio.append(el["ratio"])
    file = open(f'temp/{music_id}.json', 'a')
    # file = open(f'noise/output_Noise.json', 'a')
    file.write(json.dumps(main_list, ensure_ascii=False, indent=4))
    min_r = min(list_ratio)
    avg_r = sum(list_ratio) / len(list_ratio)
    final_info = {
        "idS3": music_id,
        "songLyrics": main_list,
        "meta": {},
        "published": 'true',
        "Author": 'Untitled',
        "Title": "Untitled",
        "minRatio": min_r,
        "averageRatio": avg_r,
        "language": lang}
    '''for file in glob('/temp/*.mp3'):
        os.remove(file)'''
    if get_table_from_graphql('Music', music_id):
        create_entry('Music', final_info)
    else:
        personal_id = get_table_from_graphql('Music', music_id)[0]['data']['id']
        update_entry('Music', personal_id, final_info)
    return final_info
