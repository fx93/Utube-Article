from googleapiclient.discovery import build
import requests
import xml.etree.ElementTree as Et
import os

DEVELOPER_KEY = "TYPE YOUR GENERATED API KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


def run(param_id, param_type, param_format):
    if param_type.lower() == "playlist":
        out_dir = './CC'
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        vid_list = fetch_all_video_ids(param_id)

        for i in range(len(vid_list)):
            heading = title(vid_list[i])
            txt_list = download_captions(vid_list[i], param_format)
            if param_format.lower() == "subtitle":
                name = '{}-{}.srt'.format(i, heading)
            else:
                name = '{}-{}.txt'.format(i, heading)
            out_name = os.path.join(out_dir, name)
            file_writer(out_name, txt_list)

    elif param_type.lower() == "single":
        tag = title(param_id)
        list_txt = download_captions(param_id, param_format)
        if param_format.lower() == "subtitle":
            file_writer('0-{}.srt'.format(tag), list_txt)
        else:
            file_writer('0-{}.txt'.format(tag), list_txt)

    else:
        print_help()


def fetch_all_video_ids(playlist_id):
    playlist_response = youtube.playlistItems().list(
        part="id,snippet",
        playlistId=playlist_id,
        maxResults="50"
    ).execute()
    video_ids = []
    for search_result in playlist_response.get("items", []):
        if search_result["kind"] == "youtube#playlistItem":
            video_ids.append(search_result['snippet']['resourceId']['videoId'])
    return video_ids


def file_writer(file_name, txt_content):
    file = open(file_name, "a")
    file.writelines(txt_content)
    file.close()


def download_captions(vdo_id, arg):
    t_list = []
    captions_url = "https://www.youtube.com/api/timedtext?lang={}&v={}".format('en', vdo_id)
    cc_response = requests.get(url=captions_url)
    cc_content = Et.fromstring(cc_response.content)

    for tag in cc_content:
        t_list.append(tag.text)
        t_list.append(" ")

    if arg.lower() == 'subtitle':
        cc_lst = convert_to_srt(cc_content, t_list)
        return cc_lst
    else:
        return t_list


def convert_to_srt(content, list_t):
    lst, tym_lst = [], []
    for item in content:
        values = item.attrib.get('start')
        tym_lst.append(values)
    mint, hrs, tym_set = 0, 0, []
    for i in range(len(tym_lst)):
        a = float(tym_lst[i]) * 1000
        b = int(a)
        if b >= 60000:
            mint = b // 60000
            b = b % 60000
        if mint >= 60:
            hrs = mint // 60
            mint = mint % 60
        c = format(b, ',d')
        if len(c) == 5:
            c = '0' + c
        tym_set.append('{:02}:{:02}:{}'.format(hrs, mint, c))
    tym_set.append('00:00:00,000')
    for x in range(len(tym_set) - 1):
        lst.append('{} \n'.format(x + 1))
        lst.append(tym_set[x] + ' --> ' + tym_set[x + 1] + '\n')
        lst.append(list_t[2 * x] + '\n')
        lst.append('\n')
    return lst


def title(vdo_id):
    topic = ''
    vdo_response = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=vdo_id
    ).execute()
    for result in vdo_response.get("items", []):
        topic = result['snippet']['title']
    return topic


def print_help():
    print("===== Usage =====")
    print('\nEnter your parameters on run function which is mentioned under main function')
    print('\n paramType is about whether this script has to download captions from an individual item or a playlist')
    print('User must enter the input as Single or Playlist')
    print('\n paramFormat is about downloading the captions for article text or srt-formatted subtitle')
    print('User must enter the input as Subtitle or Article')
    print('\n paramId is about the specific Youtube Id for a playlist or an individual item')
    print('For example, if the URL is youtube.com/watch?v=FZGugFqdr60&list=PL8dPuuaLjXtNlUrzyH5r6jN9ulIgZBpdo&index=8')
    print('Then the playlist id is - PL8dPuuaLjXtNlUrzyH5r6jN9ulIgZBpdo')
    print('Then the video id for that individual item is - FZGugFqdr60')


if __name__ == "__main__":
    run('paramId', 'paramType', 'ParamFormat')
    pass
