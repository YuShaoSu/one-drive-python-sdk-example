from onedrivesdk.helpers import GetAuthCodeServer
from onedrivesdk import get_default_client
from PIL import Image
import multiprocessing as mp
from config import client_id, client_secret, scopes, redirect_uri
from tqdm import trange

def connect():
    client = get_default_client(client_id=client_id, scopes=scopes)
    auth_url = client.auth_provider.get_auth_url(redirect_uri)
    #this will block until we have the code
    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
    client.auth_provider.authenticate(code, redirect_uri, client_secret)
    return client

def shell(path):
    if path == '':
        path = '/'
    return input(path + ' $ ').split(' ')

def ls(client, item_id, path):
    items = client.item(id=item_id).children.get()
    item_dict = {}
    folder_dict = {}
    name = {}
    print(path)
    for count, item in enumerate(items):
        name[str(count+1)] = item.name
        if item.folder is not None:
            folder_dict[str(count+1)] = item.id
        else:
            item_dict[str(count+1)] = item.id
        print('{} {}'.format(
            count + 1, item.name if item.folder is None else '/' + item.name))
    print('')
    return item_dict, folder_dict, name

def show(client, item_id):
    if len(client.item(id=item_id).thumbnails.get()) == 0:
        print('Error: File doesn\'t have thumbnail\n')
        return
    client.item(id=item_id).thumbnails[0].medium.download('./tmp_thumb.jpg')
    image = Image.open('./tmp_thumb.jpg')
    image.show()


def download(client, item_id, item_name):
    # directory = input("Enter download directory (can be relative): ")
    for i in trange(0, len(item_id)):
        client.item(id=item_id[i]).download('./' + item_name[i])


def delete(client, item_id, path, name, current_id):
    confirm = input('Are you sure you want to delete ' + path + name + '? Y/N: ')
    if confirm == 'Y':
        client.item(id=item_id).delete()    


def help():
    print('Command list:')
    print('l + INDEX\tlist\t\tList all item under the folder.')
    print('s + INDEX\tshow\t\tView thumbnails for an item.')
    print('d + INDICES\tdownload\t\tDownload multiple files, each seperate by a space.')
    print('rm + INDICES\tdownload\t\tRemove a file.')
    print('')


client = connect()

current_id = 'root'
current = ''
print('*' * 29)
print('* Welcome! Type h for help. *')
print('*' * 29, '\n')
item_dict = {}
folder_dict = {}
name = {}
item_dict, folder_dict, name = ls(client, current_id, '/')

while True:
    command = input('Please input a command: ').split(' ')

    if command[0] == 'l':
        if len(command) == 1:
            current = ''
            item_dict, folder_dict, name = ls(client, 'root', '/')
            continue
        if command[1] not in folder_dict.keys():
            if command[1] in item_dict.keys():
                print('Error: It\'s a file, not a folder!\n')
            else:
                print('Error: Folder not found.\n')
            continue
        else:
            current += '/' + name[command[1]]
            current_id = folder_dict[command[1]]
            item_dict, folder_dict, name = ls(
                client, folder_dict[command[1]], current)
    elif command[0] == 's':
        if len(command) == 1:
            print('Error: Please give an item name!\n')
        elif command[1] not in item_dict.keys():
            print('Error: File not found.\n')
        else:
            show(client, item_dict[command[1]])
    elif command[0] == 'd':
        if len(command) == 1:
            print('Error: Please give an item name!\n')
        else:
            item_list = []
            name_list = []
            for i in range(1, len(command)):
                if command[i] not in item_dict.keys():
                    print('Error: File index ', command[i], ' not found.\n')
                else:
                    item_list.append(item_dict[command[i]])
                    name_list.append(name[command[i]])
                if len(item_list) != 0:
                    download(client, item_list, name_list)
    elif command[0] == 'rm':
        if len(command) == 1:
            print('Error: Please give an item name!\n')
        else:
            if command[1] not in item_dict.keys():
                print('Error: File index ', command[1], ' not found.\n')
            else:
                delete(client, item_dict[command[1]], current, name[command[1]], current_id)
                item_dict, folder_dict, name = ls(client, current_id, current)

    elif command[0] == 'h':
        help()
    
