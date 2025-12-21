# Allmänt

## Inledning

Denna app finns till för att stimulera fågelskådning och artrace i Stockholms betong. 

Just nu visar den obsar per dag, för idag och alla tidigare dagar, i betongen. För att se vad som är gränserna för betongen så finns det en [karta](/maps). Det är den mytomspunna betongkommittén som bestämt de gränserna. Betongkommitténs ord är lag.

Men [SthlmBetong BAND](https://www.band.us/@sthlmbetong) då? Det är utmärkt verktyg för att ha koll på betonglarm och även larma när du ser att en Alpseglare sveper in över Södersjukhuset eller en Ringnäbbad mås käkar pommes i Kungsan. Ja, det ska du så klart larma på [Club300:s Bird Alarm](https://club300.se/bird-alarm/om-bird-alarm/) också!

Denna app är ett komplement till SthlmBetong BAND. Den är i ett första steg avsedd att bara göra det enkelt att ha koll på vad som rapporterats idag och andra dagar i betongen. Vilken glädje att kunna se vad som rapporterades i betongen vilken dag som helst, t.ex. [den 15 maj, 2005](/?date=2005-05-15)!

## Var kommer uppgifterna ifrån?

Uppgifter om obsar kommer från Artportalen och hämtas via Artportalens API. Sökningen i API:et görs med en så kallad geopolygon, som just beskriver gränserna för SthlmBetong. Det är samma geopolygon som använts i denna [karta](/maps).

Från att en obs registreras i Artportalen tar det några minuter innan den är tillgänglig via API:et och kan visas i denna app.

Eftersom Artportalen även innehåller obsar gjorda i svenska iNaturalist, och de är tillgängliga via API:et, så visas även iNaturalist-obsar i denna app. För mer information om Artportalens samverkan med iNaturalist se [denna artikel](https://www.slu.se/artdatabanken/om-oss/samverkan/internationell-samverkan/inaturalist/).

## Visas verkligen alla uppgifter om obsar i Artportalen?

Njä. Det finns lite utmaningar för denna app, beroende på vilka uppgifter man kan få ut via Artportalens API.

Dels får man inte ut unika id:n för observatörer. Det innebär att man inte kan skilja på två olika observatörer med samma presentationsnamn. Det är ett problem för personer med vanligare namn, som t.ex. "Anna Svensson". Finns det två "Anna Svensson" så ser det ändå ut som samma observatör. Synd om man vill sammanställa listor.

Dessutom så grupperas obsar för rariteter i Artportalen ihop i en huvudobservation, med den eller de observatörer som först rapporterade den ovanliga fågeln. Den huvudobservationen innehåller sedan underobservationer för de övriga observatörer som sedan observerade fågeln. Idag ser det inte ut som om man inte hämta ut underobservationerna via API:et. Synd om man vill sammanställa listor.
 
## Framtiden

Ja, tänk om man kunde spå in i framtiden! Några tänkta funktioner i denna app är:
* Färg- och stilmarkera obsarna, baserat på raritetsklassificering.
* Kunna filtrera och sortera obsar baserat på raritet, observationstid, stadsdel, lokal observatör etc.
* Placera ut obsarrna i kartan.
* Hämta obsar från eBirds API.
* Det ska finnas fler "microområden" än SthlmBetong, och macroområden som t.ex. "Nationalstadsparken" och "Stockholms rapportområde."
* Sökfunktion, så man kan söka på alla obsar av Kaspisk trut, eller alla obsar på sjungande Busksångare. På tidsintervall, observatörer, stadsdelar och lokaler.
* Man ska kunna registrera ett konto och registrerade användares obsar ska sammanställas i listor; totallistor, årslistor, månadslistor, stadsdelslistor och lokallistor som Skinkanlistan och Kungsanlistan!
* Det ska finnas beskrivningar av microlokalerna i betongen; Skinkan, Tanto, Observatorielunden, Skeppsbrokajen, Strömmen och andra heta lokaler i betongen.

## Historia

För länge sedan fanns det en annan webbsajt för SthlmBetong, men den försvann pga anledningar. Det kommer att komma mer information om både den webbsajten och hela SthlmBetong som idé, koncept och livsstil!

