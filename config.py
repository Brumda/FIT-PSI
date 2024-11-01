SERVER_CONFIRMATION = ''    #<16-bitové číslo v decimální notaci>\a\b. Zpráva s potvrzovacím kódem. 
                            #Může obsahovat maximálně 5 čísel a ukončovací sekvenci \a\b.
SERVER_MOVE	= '102 MOVE\a\b'	#Příkaz pro pohyb o jedno pole vpřed
SERVER_TURN_LEFT = '103 TURN LEFT\a\b'	#Příkaz pro otočení doleva
SERVER_TURN_RIGHT = '104 TURN RIGHT\a\b'	#Příkaz pro otočení doprava
SERVER_PICK_UP =	'105 GET MESSAGE\a\b'	#Příkaz pro vyzvednutí zprávy
SERVER_LOGOUT =	'106 LOGOUT\a\b'	#Příkaz pro ukončení spojení po úspěšném vyzvednutí zprávy
SERVER_KEY_REQUEST = '107 KEY REQUEST\a\b'   #Žádost serveru o Key ID pro komunikaci
SERVER_OK = '200 OK\a\b'	#kladné potvrzení
SERVER_LOGIN_FAILED = '300 LOGIN FAILED\a\b'    #Nezdařená autentizace
SERVER_SYNTAX_ERROR = '301 SYNTAX ERROR\a\b'    #Chybná syntaxe zprávy
SERVER_LOGIC_ERROR = '302 LOGIC ERROR\a\b'  #Zpráva odeslaná ve špatné situaci
SERVER_KEY_OUT_OF_RANGE_ERROR = '303 KEY OUT OF RANGE\a\b'  #Key ID není v očekávaném rozsahu

CLIENT_RECHARGING =	b'RECHARGING'	#Robot se začal dobíjet a přestal reagovat na zprávy.
CLIENT_FULL_POWER =	b'FULL POWER'	#Robot doplnil energii a opět příjímá příkazy.

#Maximální délka zpráv mínus ukončovací sekvence
CLIENT_USERNAME_LEN = 20 - 2
CLIENT_KEY_ID_LEN = 5 - 2 
CLIENT_CONFIRMATION_LEN = 7 - 2
CLIENT_MOVE_OPERATIONS = 12 - 2
CLIENT_MESSAGE_LEN = 100 - 2

#Délka timeoutu
TIMEOUT = 1
TIMEOUT_RECHARGING = 5

#Klíče
CLIENT_KEY = {"0" : 32037, "1" : 29295, "2" : 13603, "3" : 29533, "4" : 21952}
SERVER_KEY = {"0" : 23019, "1" : 32037, "2" : 18789, "3" : 16443, "4" : 18189}

#Pohyb robota
UNINITIALIZED = -1
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3