import omf, os, web, json

def sigh():
	return 'SIGH'

def transmissionConvert(owner, modelName):
	'Assume that PNNL creates a new transmission model folder.' + \
	'Also they need to place a .m file in that folder called convertMe.m' + \
	'Then they send a get request to this route.'
	# Model folder full path.
	modelDir = os.path.join(omf.omfDir, 'data', 'Model', owner, modelName)
	# Remove the existing file.
	existingOmts = [x for x in os.listdir(modelDir) if x.endswith('.omt')]
	for f in existingOmts:
		try:
			os.remove(os.path.join(modelDir,f))
		except:
			pass # Ignore deletion failure.
	# Convert and lay out the new file.
	netJson = omf.network.parse(os.path.join(modelDir, 'convertMe.m'), filePath=True)
	nxG = omf.network.netToNxGraph(netJson)
	newNetwork = omf.network.latlonToNet(nxG, netJson)
	with open(os.path.join(modelDir,'case.omt'),'w') as outFile:
		json.dump(newNetwork, outFile)
	# Rewrite allInputData.json
	with open(os.path.join(modelDir, 'allInputData.json'),'r+') as inFile:
		inData = json.load(inFile)
		inData['networkName1'] = 'case'
		inFile.seek(0)
		json.dump(inData,inFile)
		inFile.truncate()
	return 'CONVERTED'

def powerPublish(owner, modelName):
	return 'PNNL PUBLICATION URL GOES HERE'

if __name__ == '__main__':
	template_files = ['templates/'+ x  for x in web.safeListdir('templates')]
	model_files = ['models/' + x for x in web.safeListdir('models')]
	# Add routes.
	web.app.add_url_rule('/sigh', 'sigh', view_func=sigh)
	web.app.add_url_rule('/transmissionConvert/<owner>/<modelName>/', 'transmissionConvert', view_func=transmissionConvert)
	web.app.add_url_rule('/publishModel/<owner>/<modelName>/', 'powerPublish', methods=["POST"], view_func=powerPublish)
	# def crash(): raise Exception
	# web.app.add_url_rule('/crash','crash',view_func=crash)
	# Remove the bogus old publishModel route.
	allRules = web.app.url_map._rules
	del web.app.url_map._rules_by_endpoint['publishModel']
	for index, rule in enumerate(allRules):
		if rule.endpoint == 'publishModel':
			delIndex = index
	del allRules[delIndex]
	# Start the server.
	web.app.run(
		host='0.0.0.0',
		port=5001,
		threaded=True,
		extra_files=template_files + model_files,
		# debug=True
	)