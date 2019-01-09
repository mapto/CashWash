import string

from alias import alias
import string

from legal_forms import legal_forms

def normalize(name, jurisdiction = None):
	# remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
	str_from = string.punctuation + string.ascii_lowercase
	str_to = ' '*len(string.punctuation) + string.ascii_uppercase
	translator = str.maketrans(str_from, str_to)

	#tokens = nltk.word_tokenize(name.translate(translator))
	tokens = name.translate(translator).split(" ")
	words = []; letters = []
	for x in tokens:
		if len(x) == 1:
			letters.append(x)
		else:
			if letters:
				words.append("".join(letters))
				letters = []
			words.append(x)
	if letters:
		words.append("".join(letters))

	result = []
	if jurisdiction and jurisdiction in legal_forms.keys():
		result = [w for w in words if w not in legal_forms[jurisdiction]]
		#for x in words:
		#	if x not in legal_forms[jurisdiction]:
		#		result.append(x)
	else:
		result = words	
	'''
	if words[-1] in legal_form:
		words = words[:-1]
	'''
	return " ".join(result)

def clean_name(name, jurisdiction=None):
	result = normalize(name, jurisdiction)
	return alias[result] if result in alias else result

def clean_names(df):
	"""Cleans the names in a laundromat dataframe.
	Returns the result in a copy of the dataframe.
	"""

	def clean_cell(df, row, col):
		"""in place"""
		# result = normalize(df.at[row, col])
		# df.at[row,col] = alias[result] if result in alias else result
		
		df.at[row,col] = clean_name(df.at[row,col])
		# print("%s\t\t%s"%(df.at[row, col],result))

	df2 = df.copy()

	for idx, row in df2.iterrows():
		clean_cell(df2, idx, 'payer_name')
		clean_cell(df2, idx, 'beneficiary_name')

	return df2

