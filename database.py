import csv
from operator import itemgetter

# db code:
def write_db(db_file_name, data_base, field_names):
  with open(db_file_name, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(field_names)
    for key, dict_items in data_base.items():
      row = []
      for identifier, value in dict_items.items():
        row.append(value)

#            print(row)
      writer.writerow(row)

def write_db_w_insert(db_file_name, data_base, field_names, new_row, insert_idx):
  insert_performed = False
  with open(db_file_name, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(field_names)
    row_idx = 0
    for key, dict_items in data_base.items():
      row = []
      # insert new row
      if(row_idx == insert_idx):
        for identifier, value in new_row.items():
          row.append(value)
        writer.writerow(row)
        row = []
        insert_performed = True
      for identifier, value in dict_items.items():
        row.append(value)

#            print(row)
      row_idx+=1
      writer.writerow(row)
    
    # if insert has not been performed yet then it must be at the end of the file
    row = []
    if not insert_performed:
      for identifier, value in new_row.items():
        row.append(value)
      writer.writerow(row)

#def sort_and_trim(top_songs_db, num_songs):
  #db_len = len(top_songs_db)
  #dict(sorted(top_songs_db.items(), key='shares'))


def get_top_songs(db_file_name):
  db_size, fieldnames, song_recommend_db = read_db(db_file_name)
  new_dictionary_arry = []
  # convert from db to array
  for key, items in song_recommend_db.items():
    items['shares'] = int(items['shares'])
    new_dictionary_arry.append(items)
  top_songs_dictionary_arry = sorted(new_dictionary_arry, key=itemgetter('shares'), reverse = True)
  # for items in top_songs_dictionary_arry:
  #   artist = items['artist']
  #   print(f'artist = {artist}')
  # print(top_songs_dictionary_arry)

  return top_songs_dictionary_arry
      
def read_db(db_file_name):
  reader = csv.DictReader(open(db_file_name))
  song_recommend_db = {}
  row_count = 0
  
  #   print(reader.fieldnames)
  for row in reader:
    key = row_count
    song_recommend_db[key] = row
    row_count += 1
  #print(song_recommend_db[0]['artist'])
  db_size = len(song_recommend_db)
  return db_size, reader.fieldnames, song_recommend_db


def add_song_to_database(data_base_name, artist, track, id):
  
  db_size, field_names, song_recommend_db = read_db(data_base_name)
  share_count = 1
  print("\n\n Entering search function\n")
  is_found, entry_idx = search_database(song_recommend_db, id)
  if(is_found):
    # increment share count
    share_count = int(song_recommend_db[entry_idx]['shares']) + 1
    song_recommend_db[entry_idx]['shares'] = share_count
    write_db(data_base_name, song_recommend_db, field_names)
  else:
    # add new entry
    if(song_recommend_db[entry_idx]['id'] < id):
      entry_idx += 1
    print(f"row to insert {entry_idx}")
    new_entry = {}
    new_entry['artist'] = artist
    new_entry['track'] = track
    new_entry['id'] = id
    new_entry['shares'] = share_count
    write_db_w_insert(data_base_name, song_recommend_db, field_names, new_entry, entry_idx)

  return share_count

def search_database(song_recommend_db, id):
  database_size = len(song_recommend_db)
  lower_bound = 0
  upper_bound = database_size - 1
  found = False
  current_entry = round((lower_bound + upper_bound)/2)
  while((lower_bound <= upper_bound) and (found == False)):
    db_entry = song_recommend_db[current_entry]
    #print(f"current entry {current_entry}")
    #print(db_entry)
    if(db_entry['id'] == id):
      found = True
      print("found")
    elif(db_entry['id'] < id):
      lower_bound = current_entry + 1
      current_entry = round((lower_bound + upper_bound)/2)
    else:
      upper_bound = current_entry - 1
      current_entry = round((lower_bound + upper_bound)/2)

  return found, current_entry

if __name__ == '__main__':
  print("\nTesting database\n")
  # field_names, song_recommend_db = read_db("spotify\song_list.csv")
  # print("Database read\n")

  # song_recommend_db = []
  # new_entry = {}
  # new_entry['artist'] = "Metallica"
  # new_entry['track'] = "Enter Sandman"
  # new_entry['id'] = "id1"
  # song_recommend_db.append(new_entry)
  # field_names = {'artist', 'track', 'id'}

  # write_db("song_list.csv", song_recommend_db, field_names)
  # print("Database written\n")
  #add_song_to_database("song_list.csv", "new artist", "new song", "2newid")
  sorted_db = get_top_songs("song_list.csv")