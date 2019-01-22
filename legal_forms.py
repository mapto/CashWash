'''
A country-driven directory of legal names
Whereas for many companies English names are used, there's also a list of names in the original language

Sources:
AE: http://www.infoprod.co.il/country/uae2b.htm
BE: https://www.companyformationbelgium.com/types-of-belgian-companies
CH: https://www.startups.ch/en/inform/details/forms/
EE: https://itscorporate.ee/en/legal-forms-of-estonian-company/
ES: https://www.mariscal-abogados.com/legal-forms-of-company-formation-in-spain/
FI: https://www.companyformationfinland.com/types-of-companies-finland
HU: https://smartlegal.hu/publication/company-forms-in-hungary
'''

legal_forms = {\
	"AE": ["INC", "LLC", "LIMITED", "FZE"],\
	"AI": ["LLP"],\
	"AT": ["GMBH", ],\
	"AZ": ["LTD", "LLC", "LIMITED LIABILITY COMPANY"],\
	"BE": ["BVBA", "NV"],\
	"BG": ["AD", "EAD", "LTD", "JSC"],\
	"BM": ["LTD"],\
	"BR": ["LTDA"],\
	"BY": ["LTD", "OAO"],\
	"CA": ["CORP", "INC", "SA"],\
	"CH": ["AG", "SA", "GMBH"],\
	"CN": ["LIMITED", "LTD"],\
	"CY": ["LIMITED", "LTD"],\
	"CZ": ["AS", "SRO", "DOO"],\
	"DE": ["AG", "GMBH", "UG"],\
	"DK": ["AS"],\
	"DM": ["INC"],\
	"EC": [],\
	"EE": ["AS"],\
	"ES": ["SL", "SA", "SCA", "SPA", "SCL"],\
	"FI": ["OÜ", "OY", "OYJ"],\
	"FR": ["SAS", "SPA"],\
	"GB": ["LLP", "LTD", "LP", "LIMITED", "INC"],\
	"GE": ["LTD", "LLC"],\
	"GR": ["INC"],\
	"HK": ["LIMITED", "LTD"],\
	"HR": ["DOO"],\
	"HU": ["KFT"],\
	"IE": ["LTD"],\
	"IL": ["LTD"],\
	"IN": ["LTD"],\
	"US": ["INC", "HOLDING"]\
}
