# Personuppgiftspolicy

## 1. Inledning

Denna instans av [microbirding](https://github.com/pacoispaco/microbirding)-appen (fortsattningsvis kallat "denna tjänst") driftas på en virtuell [Digitalocean](https://www.digitalocean.com/) server i Nederländerna. Inga personuppgifter lagras i denna tjänst eller på någon server.

## 2. Hämtning och behandling av personuppgifter

Uppgifter om obsar hämtas från Artportalen, och de uppgifter som hämtas och visas om individuella obsar i denna tjänst är en delmängd av de uppgifter som visas på Artportalens webbsajt i öppet och oinloggat läge. Det gäller även personuppgifter. Ingen övrig bearbetning eller lagring av personuppgifterna görs i denna tjänst. Personuppgifter i denna tjänst hanteras i enlighet med [beskrivningen av behandling av personuppgifter på Artportalen](https://www.slu.se/artdatabanken/om-oss/behandling-av-personuppgifter).

Hämtningen av uppgifter görs via Artportalens API och med en officiell och godkänd API nyckel utfärdad av Artportalen. 

## 3. Identifiering av personer

Via Artportalens API kan man inte hämta användarunika id:n utan enbart observatörernas namn. Eftersom observatörsnamn inte är garanterat unika, kan två olika observatörer i denna tjänst inte entydigt identifieras och särskiljas. Men eftersom namn står i anslutning till obsar som har geografisk position, så kan kombinationen av namn och position på obs användas för att identifiera en person.

## 4. Borttagning och korrigering av personuppgifter

Eftersom alla personuppgifter hämtas från Artportalen, är det Artportalen du ska kontakta om du vill att dina uppgifter ska tas bort eller korrigeras. Kontaktuppgifter finns i [beskrivningen av behandling av personuppgifter på Artportalen](https://www.slu.se/artdatabanken/om-oss/behandling-av-personuppgifter).

## 5. Kakor och loggar

Denna tjänst använder sig inte av kakor (eng: cookies). Den använder sig av lokal lagring (eng: local storage) för att spara om du valt att köra light eller dark mode. Den sparar åtkomstloggar som innehåller uppgifter om anropares IP-adress. Åtkomstloggar raderas enligt ett rullande schema och loggfiler behålls i tidsordning, men raderas i tidsordning när loggfilerna nått en viss sammanlagd storlek.

## 6. Webbanalys

Denna tjänst använder [Umami](https://umami.is/) för anonym och integritetsvänlig webbanalys. Umami använder inga kakor och lagrar inga personuppgifter. IP-adresser anonymiseras och uppgifterna används enbart för övergripande statistik om användning av tjänsten. All analysdata lagras på samma server som denna tjänst driftas (se ovan).
