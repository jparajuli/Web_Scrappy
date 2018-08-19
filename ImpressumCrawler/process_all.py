import re
from fuzzywuzzy import fuzz, process
possible_street_hints =['Am', 'Strasse', 'Straße', 'strasse', 'straße', 'str.', 'Str.', 'anlage', 'hof']
german_company_endings = '^(ag|gmbh|ggmbh|group|copmany|gbr|e\.v\.|e\.g\.|llc|architekten|gruppe|se)$'
regexp_com_name = '((?:[A-Z0-9\-&\+]\.?\w*\s?(?:[a-z0-9\-]\w*\s?)?)+\s(?:{0}$))'.format(german_company_endings)
regexp_email = '([\w\.-]+(?:@|\s?\(\s?at\s?\)\s?)[\w\.-]+)'
regexp_fax = '((?:[Ff]ax|[Tt]elefax).+\d+)'
regexp_strasse = '((?:[a-zA-ZäöüÄÖÜß]\D*)\s+\d+?\s*.*)'
regexp_tele = '((?:[Tt]el[\:\.]?|[Ff]on\:?|[Pp]hone\:?|[Tt]elephone\:?)?\s?\(?\+?\s?\d{1,5}\)?\s?[/\-]?\s?\(?\d{1,5}\)?\s?[/\-]?\s?\d{2,6}\s?[/\-]?\s?\d{1,5}\s?[/\-]?\s?\d{1,3}\s?[/\-]?\s?\d{1,3})'
class ProcessAll:
    def __init__(self, response_data):
        self.response_data = response_data

    def text_processing(self):
        #response_all = [s.strip() for s in self.response_data]
        response_all = [s.strip() for s in self.response_data if (len(s)!=0) & (len(s)<=100)]
        response_all = [re.sub("\s\s+" , " ", s) for s in response_all]
        response_all = [re.sub("\xa0"," ", s) for s in response_all]
        punct = '!"#$%\'*;<=>?[\\]^_`{|}~–'
        table=str.maketrans('','',punct)
        stripped_data = [w.translate(table) for w in response_all]
        stripped_data=[s for s in stripped_data if (s !=' ') &(s!='\n') &(s!='\t') &(s!='')]
        stripped_data = [s.strip() for s in stripped_data]
        return stripped_data

    def process_comp_names(self):
        stripped_data = self.text_processing()
        splitted_data = [s.split() for s in stripped_data]
        splitted_data = [s for s in splitted_data if (s!=[]) & (1<len(s)<=5)]
        prob_comp_names =[s for s in splitted_data if re.match(german_company_endings,s[-1].lower())]
        prob_comp_names =[' '.join(s) for s in prob_comp_names]
        comp_names= max(set(prob_comp_names), key=prob_comp_names.count)
        return comp_names

    def process_emails(self):
        stripped_data = self.text_processing()
        emails =  list(set([w[0] for w in [re.findall(regexp_email,s) for s in stripped_data] if w!=[]]))
        emails_new=[]

        if not any([s.startswith(('info','impressum','imprint','kontakt')) for s in emails]):
            emails_new = emails
        else:
            emails_new = [s for s in emails if s.startswith(('info','impressum','imprint','kontakt'))]
        emailss = ','.join(emails_new)
        return emailss
    def process_fax(self):
        stripped_data = self.text_processing()
        faxs =  list(set([w[0] for w in [re.findall(regexp_fax,s) for s in stripped_data] if w!=[]]))
        if faxs:
            fax = faxs[0]
        else:
            fax =''
        return fax
    def process_telephone(self):
        stripped_data = self.text_processing()
        telephone =  list(set([w[0] for w in [re.findall(regexp_tele,s) for s in stripped_data] if w!=[]]))
        telephone_new =[]
        if not any ([s.lower().startswith(('fon','phone','tel')) for s in telephone ]):
            telephone_new = list(set([s for s in telephone if len(''.join(s.split()))>=11]))
        else:
            telephone_new =list(set([s for s in telephone if s.lower().startswith(('fon','phone','tel'))]))
        telephone_new = ','.join(telephone_new)
        return telephone_new
    def process_address(self):
        stripped_data = self.text_processing()
        strassen = list(set([w[0] for w in [re.findall(regexp_strasse,s) for s in stripped_data] if w!=[]]))
        strassen = [s for s in strassen if len(s.split())<=5]
        strassen = [s for s in strassen if len(s)<50]
        if not any([s.lower().find('str')!=-1 for s in strassen]):
            strassen_new = strassen
        else:
            strassen_new = [s for s in strassen if s.lower().find('str')!=-1]
        if len(strassen_new)==1:
            possible_strassen = strassen_new
        else:
            possible_strassen = []
            for k in strassen_new:
                fuzz_ratio = [(fuzz.partial_ratio(s,k)) for s in possible_street_hints]
                if max(fuzz_ratio)> 95:
                    possible_strassen.append(k)
                else:
                    pass
        possible_plz_index = [stripped_data.index(s) for s in possible_strassen]
        possible_com_name = [stripped_data[s-1] for s in possible_plz_index]
        possible_plz = [stripped_data[s+1] for s in possible_plz_index]
        possible_address = [possible_com_name[s]+','+possible_strassen[s]+','+possible_plz[s] for s in range(len(possible_plz))]
        return possible_address
