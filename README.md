**Účel**

Služba na generovanie obrázkov GIF s pseudonáhodným obsahom, ktorý závisí od jedného parametra.

**Inštalácia a nástroje**

Chýbajúce moduly tretích strán je potrebné nainštalovať pomocou pipu:
`pip install jinja2 werkzeug mysql-connector-python Pillow python-dotenv`
alebo
`python -m pip install jinja2 werkzeug mysql-connector-python Pillow python-dotenv`

(Tento zoznam môže byť na inom počítači dlhší alebo kratší)

1. jinja2 - šablónovací engine na generovanie HTML stránok - https://jinja.palletsprojects.com/en/stable/
2. werkzeug - sada nástrojov WSGI - https://werkzeug.palletsprojects.com/en/stable/
3. mysql.connector - pripojenie MySQL pre Python - https://dev.mysql.com/doc/connector-python/en/quick-installation-guide.html
4. Pillow - generovanie obrázkov - https://pillow.readthedocs.io/en/stable/
5. python-dotenv - čítanie súboru .env z koreňového adresára projektu

**DB**

Pred spustením je potrebné vytvoriť databázu vo vašej lokálnej inštalácii MySQL.
Parametre prístupu k databáze sú uvedené v súbore .env v koreňovom adresári projektu. Ak ju chcete vytvoriť, skopírujte súbor .env.example do súboru .env a zadajte svoje používateľské meno a heslo.
Inicializačný súbor databázy (init.sql) sa nachádza v koreňovom adresári projektu.

**Spustiť**

Príkaz na spustenie webovej služby
`python src/anno.py`
Spúšťa sa na porte 5555 a počúva na všetkých IP adresách (0.0.0.0).
http://localhost:5555/ vedie priamo do administračného panela. http://localhost:5555/testing_get - stránka na testovanie požiadaviek GET
http://localhost:5555/testing_post - stránka na testovanie požiadaviek POST
Ak sa najprv prihlásite do administračného panela, testovacie stránky sa otvoria pre toho istého používateľa.
Ak sa neprihlásite, použije sa používateľ s id=1. Tento používateľ sa nazýva „test“.
Je to skutočný používateľ z databázy.
Má len trochu špeciálnu rolu.
Predpokladá sa, že jeho prihlasovacie meno a heslo sú známe všetkým.

Pri generovaní testovacích stránok sa tieto hodnoty prihlasovacieho mena a hesla odovzdajú do šablónového enginu, ak neexistuje žiadny iný používateľ s platnou reláciou.

**Použitie**

Predtým, ako používateľ začne prijímať obrázky GIF, musí sa overiť vo webovej službe.
Toto nie je to isté ako overenie vo webovom rozhraní programu.
Ide o samostatnú požiadavku POST do webovej služby.
Klient odošle svoje používateľské meno a heslo a dostane overovací token vygenerovaný pre konkrétne ID používateľa.
Toto ID používateľa je potom možné extrahovať z tokenu na overenie jeho vlastníctva.
Token klient uloží do globálnej premennej `window.gifMakerAuthToken`.
Následne sa použije na generovanie samotných súborov GIF.
*Dôležitá funkcia*: tajný kód na generovanie tokenu sa náhodne generuje pri spustení webovej služby.
Preto sa po reštarte webovej služby všetky predtým vydané autentifikačné tokeny stanú neplatnými.
Toto je možné opraviť nahradením náhodného čísla pevným tajným reťazcom. Nie je to však potrebné opravovať.

Administrátorský používateľ a používateľ webovej služby sú v databáze fyzicky rovnakými používateľmi.
Používajú sa však rôzne autentifikačné postupy.
Autentifikácia v administrátorskom paneli vytvorí záznam v tabuľke admin_sessions v databáze. Tento záznam môže byť zastaraný.
Autentifikácia v samotnej webovej službe vytvorí token, ktorý nie je uložený v databáze, ale je možné ho overiť nezávisle.

S autentifikačným tokenom môžete zadávať skutočné požiadavky na generovanie animovaných obrázkov.
Existujú dva spôsoby, ako to urobiť:
1. Požiadavka POST. Telo požiadavky je JSON. Odpoveď je tiež „application/json“.
Jedným z polí odpovede je URL adresa, kde je uložený výsledok.
Samotný výsledok sa potom musí načítať na stránku so samostatnou požiadavkou alebo niekde uložiť ako URL adresa.
Je uložený v samostatnom verejnom priečinku webovej aplikácie.
Názov výsledku je pomerne náhodný. Napríklad,
`/static/1/1790245945_1_d41d8cd98f00b204e9800998ecf8427e.gif`
/1/ - podpriečinok, ktorého názov obsahuje celočíselné ID používateľa
1790245945 - unixtime. Čas generovania súboru
1 - ID šablóny použité na generovanie
d41d8cd98f00b204e9800998ecf8427e - MD5 hash seedu použitého na generovanie
Preto neexistuje riziko, že jeden používateľ nájde súbor vygenerovaný iným používateľom hrubou silou.

2. GET požiadavka. Neexistuje žiadne telo požiadavky. Parametre požiadavky sú parametre priamo v URL. Odpoveď je „image/gif“.

Túto URL adresu je možné priamo použiť ako hodnotu atribútu src elementu <img>.
`let url1 = "http://localhost:5555/g?token=__TOKEN__&t=123&template=1";`
`jQuery('#demo1').attr('src', url1.replace('__TOKEN__', window.gifMakerAuthToken));`

Každá požiadavka vytvorí záznam v databáze. Toto sa robí na uloženie výsledku do vyrovnávacej pamäte.
Ak používateľ A vytvorí obrázok GIF typu B so zrnitosťou C, záznam o tom sa uloží do databázy.
Opakovaná požiadavka od používateľa A na obrázok typu B so zrnitosťou C vráti predtým uložený súbor,
namiesto reštartovania procesu generovania GIF. Toto výrazne zrýchľuje službu.
Ako riešenie má požiadavka na generovanie súboru GIF špeciálny príznak,
ktorý bráni webovej službe používať vyrovnávaciu pamäť a vždy vytvára nový súbor GIF.

**Testovanie**

Generátory (súbory src/gen_*) je možné spúšťať nezávisle na účely testovania.
Napríklad `python src/gen_f.py`
Predpokladá sa, že v tomto prípade