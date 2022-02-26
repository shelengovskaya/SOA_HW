from timeit import timeit  
from tabulate import tabulate 
import sys  



if __name__=='__main__':
 
    message = '''d = { 
       'float' : 1539.100, 
       'int' : 33, 
       'Name' : """MEGA_GAMER_2222""", 
       'dict': dict((str(i),i) for i in iter(range(100))),   
       'words': """ 
           Pentos is a large port city, more populous than Astapor on Slaver Bay,  
           and may be one of the most populous of the Free Cities.  
           It lies on the bay of Pentos off the narrow sea, with the Flatlands  
           plains and Velvet Hills to the east. 
           The city has many square brick towers, controlled by the spice traders.  
           Most of the roofing is done in tiles. There is a large red temple in  
           Pentos, along with the manse of Illyrio Mopatis and the Sunrise Gate  
           allows the traveler to exit the city to the east,  
           in the direction of the Rhoyne. 
           """ 
    }''' 

    setup_pickle = '%s ; import pickle ; src = pickle.dumps(d, 2)' % message
    setup_xml = '%s ; import dicttoxml; import xmltodict; src = dicttoxml.dicttoxml(d)' % message
    setup_json = '%s ; import json; src = json.dumps(d)' % message 
    setup_yaml = '%s ; import yaml; src = yaml.dump(d)' % message
    setup_msgpack = '%s ; import msgpack; src = msgpack.packb(d)' % message


    tests = [ 
       # (title, setup, enc_test, dec_test) 
       ('pickle (native serialization)', setup_pickle, 'pickle.dumps(d, 2)', 'pickle.loads(src)'),
       ('xml', setup_xml, 'dicttoxml.dicttoxml(d)', 'xmltodict.parse(src)'),
       ('json', setup_json, 'json.dumps(d)', 'json.loads(src)'), 
       ('yaml', setup_yaml, 'yaml.dump(d)', 'yaml.load(src, Loader=yaml.FullLoader)'),
       ('msgpack', setup_msgpack, 'msgpack.packb(d)', 'msgpack.unpackb(src, raw=False)'),
        

    ] 
     
    loops = 5000 
    enc_table = [] 
    dec_table = [] 
     
    print ("Running tests (%d loops each)" % loops) 
     
    for title, mod, enc, dec in tests: 
       print (title) 
     
       print ("  [Encode]", enc)  
       result = timeit(enc, mod, number=loops) 
       exec (mod) 
       enc_table.append([title, result, sys.getsizeof(src)]) 
     
       print ("  [Decode]", dec)  
       result = timeit(dec, mod, number=loops) 
       dec_table.append([title, result]) 
     
    enc_table.sort(key=lambda x: x[1]) 
    enc_table.insert(0, ['Package', 'Seconds', 'Size']) 
     
    dec_table.sort(key=lambda x: x[1]) 
    dec_table.insert(0, ['Package', 'Seconds']) 
     
    print ("\nEncoding Test (%d loops)" % loops) 
    print (tabulate(enc_table, headers="firstrow")) 
     
    print ("\nDecoding Test (%d loops)" % loops) 
    print (tabulate(dec_table, headers="firstrow"))
