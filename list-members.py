import requests, json, os, csv, pandas
from argparse import ArgumentParser
import google_auth_oauthlib.flow


list_channel="https://www.googleapis.com/youtube/v3/channels?mine=true"
list_members="https://www.googleapis.com/youtube/v3/members?part=snippet&mode=all_current&maxResults=1000&pageToken={}"
scopes = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.channel-memberships.creator"]

def persist_as_json(file_name, json_obj):
    
    try:        
        with open(file_name, "w") as output:
            json.dump(json_obj, output)
    except OSError:
        print("Error writing file: {}".format(file_name))

def fetch_members(auth_token, pageToken, list_instance=[]):
    isLastPage = False
    try:
        if pageToken == '':
            url=list_channel
        else:
            url=list_channel.format(pageToken)
        headers={"Authorization": "Bearer {}".format(auth_token), "User-Agent": "PostmanRuntime/7.26.8"}
        resp = requests.get(list_members, headers=headers)
        if resp.status.code == 200:
            result = json.loads(resp.text)
            list_instance.append(result)
            if result['nextPageToken']:
                fetch_members(auth_token, result['nextPageToken'], list_instance)
            else:
                return result
        else:
            print("error calling list channels api")
            return None
    except Exception as e:
        print("invalid authentication or params", e)
        return None


def fetch_channels(auth_token):
    try:
        url=list_channel
        headers={"Authorization": "Bearer {}".format(auth_token), "User-Agent": "PostmanRuntime/7.26.8"}
        resp = requests.get(list_channel, headers=headers)
        if resp.status.code == 200:
            result = json.loads(resp.text)
            return result
        else:
            print("error calling list channels api")
            return None
    except Exception as e:
        print("invalid authentication or params", e)
        return None
    
    

def login(secretfile):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = secretfile.strip()
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    return credentials.token

def persist_as_csv(json_file_path, csv_file_path):
    try:       
        df = pandas.read_json(json_file_path)
        df.to_csv(csv_file_path)
    except OSError:
        print("Error writing file: {}".format(csv_file_path))

def main(secretfile, outputfilename):
    token = login(secretfile)
    print("your token is: {}".format(token))
    # list channels to test oauth
    channels = fetch_channels(token)

    # list members
    members = fetch_members(fetch_members=token)
    persist_as_json('{}.json'.format(outputfilename), json.dumps(members))
    persist_as_csv('{}}.json'.format(outputfilename), '{}.csv'.format(outputfilename))
    print(json.dumps(channels))


if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument("-f", "--secretfile", dest="secretfile",
                        help="your secret json file")
    parser.add_argument("-o", "--outputfilename", dest="outputfile",
                        help="name to csv and json output files")
    
    args = parser.parse_args()
    main(args.secretfile, outputfilename)