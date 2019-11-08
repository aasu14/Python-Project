#Solution 1.
import os
import glob
import json
def merge_json(path, ip_fname, op_fname, max_size):

	os.chdir(path) 					

	i = 1
	size = 0
	result = []
	result_dict = {}

	for json_file in glob.glob(ip_fname + '*.json'):

		json_opened = open(json_file, encoding='utf-8')
		logs = json.load(json_opened)

		json_opened.seek(0,2)
		fsize = json_opened.tell()		

		key = list(logs)				
		if fsize <= max_size:			
			if size + fsize <= max_size:
				result.extend(logs[key[0]])
			else:
				result_dict[key[0]] = result[:]
				result.extend(logs[key[0]])
				outfile = open(op_fname + str(i) +'.json', 'w')
				json.dump(result_dict, outfile, ensure_ascii=False)
				i += 1
				size = 0
				result_dict = {}
				result = []
				result.extend(logs[key[0]])
			
			size += fsize
		
		else:							
			print("file "+ json_file + " is too large to write in a new file, try increasing the max size")

	if size <= max_size:
		result_dict[key[0]] = result[:]
		outfile = open(op_fname + str(i) +'.json', 'w')
		json.dump(result_dict, outfile, ensure_ascii=False)


try: 
	path = str(input("Enter path: "))
	input_base_name = str(input("Enter input json file name suffix: "))
	output_base_name = str(input("Enter the output json file name suffix: "))
	max_size = int(input("Enter the maximum file size(in bytes): "))
	merge_json(path, input_base_name, output_base_name, max_size)

except:
	print("Error occured, try entering valid parameters...")

#Solution 2.
from json import load, JSONEncoder
from optparse import OptionParser
from re import compile

float_pat = compile(r'^-?\d+\.\d+(e-?\d+)?$')
charfloat_pat = compile(r'^[\[,\,]-?\d+\.\d+(e-?\d+)?$')

parser = OptionParser(usage="""%prog [options]
Group multiple GeoJSON files into one output file.
Example:
  python %prog -p 2 input-1.json input-2.json output.json""")

defaults = dict(precision=6)

parser.set_defaults(**defaults)

parser.add_option('-p', '--precision', dest='precision',
                  type='int', help='Digits of precision, default %(precision)d.' % defaults)

if __name__ == '__main__':
    
    options, args = parser.parse_args()
    infiles, outfile = args[:-1], args[-1]

    outjson = dict(type='FeatureCollection', features=[])
    
    for infile in infiles:
        injson = load(open(infile))
        
        if injson.get('type', None) != 'FeatureCollection':
            raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)
        
        if type(injson.get('features', None)) != list:
            raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)
        
        outjson['features'] += injson['features']

    encoder = JSONEncoder(separators=(',', ':'))
    encoded = encoder.iterencode(outjson)
    
    format = '%.' + str(options.precision) + 'f'
    output = open(outfile, 'w')
    
    for token in encoded:
        if charfloat_pat.match(token):
            output.write(token[0] + format % float(token[1:]))

        elif float_pat.match(token):
            output.write(format % float(token))

        else:
            output.write(token)
