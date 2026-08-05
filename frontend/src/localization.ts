export enum Language {
  Polish = "pl",
  English = "en",
}

const localizedCopy = {
  [Language.Polish]: {
    appTitle: "Co na to Jezus?",
    homeLabel: "Co na to Jezus? — strona główna",
    header: "Refleksja oparta na Biblii",
    eyebrow: "Hm, a ciekawe",
    title1: "Co na to",
    title2: "Jezus?",
    intro:
      "Napisz, co Cię martwi. Poszukamy pomocnych fragmentów Biblii i podpowiemy, jak możesz spojrzeć na tę sytuację.",
    label: "Co na to Jezus?",
    placeholder: "Zmagam się z trudną decyzją w pracy…",
    privacy: "Opisz sytuację bez prywatnych danych innych osób.",
    submit: "Zobacz",
    loading: "Szukam odpowiedzi…",
    tipsTitle:
      "Jaśniejszy opis sytuacji pozwala stworzyć bardziej pomocną refleksję",
    tips: [
      "Najpierw opisz fakty, a potem własną interpretację.",
      "Staraj się unikać oceniających określeń i osądów.",
      "Pomiń imiona, adresy i dane pozwalające zidentyfikować osoby.",
    ],
    algorithmEyebrow: "Jak to działa",
    algorithmTitle: "Jak powstaje refleksja",
    algorithmIntro:
      "Aplikacja łączy ostrożną klasyfikację tematu, lokalne wyszukiwanie w Biblii i kontekst zweryfikowany przez człowieka. Każdy etap ogranicza ryzyko przypadkowego lub wyrwanego z kontekstu dopasowania.",
    algorithmSteps: [
      {
        title: "Najpierw bezpieczeństwo",
        body: "Opis jest sprawdzany pod kątem pilnych sygnałów samookaleczenia, przemocy lub nadużycia. Jeśli się pojawią, aplikacja wyświetla wyraźną informację o natychmiastowym wsparciu, nie rezygnując z dalszej refleksji.",
      },
      {
        title: "Rozpoznanie obszaru etycznego",
        body: "Polskie i angielskie reguły językowe szukają 21 obszarów etycznych, takich jak przebaczenie, uczciwość, uprzedzenia, granice czy odpowiedzialność. Wielojęzyczny model semantyczny porównuje sens całego opisu z zatwierdzonymi, ogólnymi profilami wzbogaconymi przez 42 abstrakcyjne podsumowania. Może dodać jeden ważny temat pominięty przez słowa kluczowe.",
      },
      {
        title: "Wyszukanie fragmentów Biblii",
        body: "Wyszukiwanie odbywa się wyłącznie w lokalnym tekście Biblii: UBG po polsku albo WEB po angielsku. Ranking łączy podobieństwo słów, podobieństwo znaczenia, ostrożne wzmocnienie zweryfikowanych powiązań tematycznych i niewielką preferencję dla Ewangelii. Słabe i powtarzające się wyniki są odrzucane.",
      },
      {
        title: "Sprawdzenie szerszego kontekstu",
        body: "Do każdego kandydata dołączana jest najwęższa pasująca karta z kolekcji 200 dwujęzycznych kontekstów zweryfikowanych przez człowieka. Pokazuje ona, skąd pochodzi fragment, jego miejsce w większej całości, pierwotne znaczenie oraz źródła użyte przy opracowaniu.",
      },
      {
        title: "Ułożenie praktycznej refleksji",
        body: "Model językowy otrzymuje tylko wybrane fragmenty i zatwierdzony kontekst. Spośród kandydatów wybiera od jednego do trzech tekstów i formułuje ostrożne odniesienie do opisanej sytuacji. Odpowiedź jest walidowana i w razie potrzeby poprawiana; bez zewnętrznego modelu działa deterministyczny wariant lokalny.",
      },
      {
        title: "Źródła i ograniczenia",
        body: "Cytaty są kopiowane bezpośrednio z lokalnego tekstu Biblii i opatrzone informacją o przekładzie. Wynik zawiera kontekst, praktyczne zastosowanie i wyraźne zastrzeżenie, że jest refleksją, a nie pewną odpowiedzią ani poradą specjalistyczną. Opis nie jest zapisywany, chyba że świadomie utworzysz link do udostępnienia.",
      },
    ],
    algorithmSafeguard:
      "Model językowy nie wybiera dowolnych cytatów i nie dopisuje własnych źródeł. Może pracować wyłącznie na fragmentach i kontekście przekazanych przez system wyszukiwania.",
    algorithmTechnicalDescription: "Bardziej techniczny opis",
    fallbackError: "Coś poszło nie tak.",
    back: "Zadaj inne pytanie",
    safetyTitle: "Zatrzymaj się i poszukaj natychmiastowego wsparcia",
    read: "Przeczytaj i zobacz szersze znaczenie",
    sources: "Fragmenty Biblii i ich kontekst",
    footerBible:
      "Cytaty: Uwspółcześniona Biblia Gdańska, © 2018 Fundacja Wrota Nadziei, CC BY-ND 4.0.",
    selectedVerse: "Wybrany werset",
    contextOrigin: "Skąd pochodzi ten fragment?",
    broaderContext: "Szerszy kontekst",
    originalMeaning: "Co znaczył pierwotnie?",
    application: "Jak odnosi się do Twojej sytuacji?",
    passageContext: "Przeczytaj całą jednostkę",
    contextSources: "Kontekst na podstawie tych źródeł",
    footerPrivacy:
      "Opis sytuacji zapisujemy tylko wtedy, gdy świadomie utworzysz link do udostępnienia.",
    analyticsText:
      "Czy zgadzasz się na anonimową analitykę, która pomaga nam ulepszać aplikację? Nie wysyłamy treści Twoich pytań.",
    analyticsAccept: "Zgadzam się",
    analyticsReject: "Nie, dziękuję",
    question: "Twoje pytanie",
    sharedQuestion: "Udostępnione pytanie",
    share: "Udostępnij",
    sharing: "Tworzę link…",
    shared: "Link skopiowany",
    ready: "Link jest gotowy",
    sharePrivacy: "Każda osoba z linkiem zobaczy to pytanie i odpowiedź.",
    sharedBadge: "Udostępniona odpowiedź",
  },
  [Language.English]: {
    appTitle: "What would Jesus do?",
    homeLabel: "What would Jesus do? — home",
    header: "A Bible-grounded reflection",
    eyebrow: "Hmm, interesting",
    title1: "What would",
    title2: "Jesus do?",
    intro:
      "Tell us what’s worrying you. We’ll find helpful Bible passages and suggest a way to look at the situation.",
    label: "What would Jesus do?",
    placeholder: "I’m struggling with a decision at work...",
    privacy: "Share the situation, not anyone’s private details.",
    submit: "See",
    loading: "Reflecting…",
    tipsTitle: "A clearer situation leads to a more useful reflection",
    tips: [
      "Describe the facts before your interpretation of them.",
      "Try to avoid judgmental language and assumptions.",
      "Leave out names, addresses, and identifying details.",
    ],
    algorithmEyebrow: "How it works",
    algorithmTitle: "How the reflection is created",
    algorithmIntro:
      "The application combines cautious theme detection, local Bible search, and human-reviewed context. Each stage reduces the risk of an accidental or out-of-context match.",
    algorithmSteps: [
      {
        title: "Safety comes first",
        body: "The description is checked for urgent signs of self-harm, violence, or abuse. When one appears, the application displays prominent immediate-support guidance while continuing to provide a reflection.",
      },
      {
        title: "Recognizing the ethical concern",
        body: "Polish and English language rules look for 21 ethical themes, including forgiveness, honesty, prejudice, boundaries, and responsibility. A multilingual semantic model compares the meaning of the whole description with approved general profiles enriched by 42 abstract summaries. It may add one important theme missed by keywords.",
      },
      {
        title: "Finding Bible passages",
        body: "Search runs only against the local Bible text: UBG in Polish or WEB in English. Ranking combines word overlap, semantic similarity, a cautious boost for reviewed thematic associations, and a small Gospel preference. Weak and repetitive results are removed.",
      },
      {
        title: "Checking the wider context",
        body: "Each candidate receives the narrowest matching card from a collection of 200 bilingual contexts reviewed by a person. It explains where the passage comes from, its place in the larger unit, its original meaning, and the sources used to prepare the context.",
      },
      {
        title: "Composing a practical reflection",
        body: "The language model receives only the selected passages and approved context. It chooses one to three candidates and writes a cautious application to the described situation. The response is validated and corrected when necessary; a deterministic local version works without an external model.",
      },
      {
        title: "Sources and limitations",
        body: "Quotations are copied directly from the local Bible text and include translation details. The result provides context, practical application, and a clear reminder that it is a reflection rather than certainty or professional advice. The description is not stored unless you explicitly create a share link.",
      },
    ],
    algorithmSafeguard:
      "The language model cannot choose arbitrary quotations or introduce its own sources. It can work only with the passages and context supplied by the retrieval system.",
    algorithmTechnicalDescription: "More technical description",
    fallbackError: "Something went wrong.",
    back: "Ask another question",
    safetyTitle: "Pause and seek immediate support",
    read: "Read and explore the wider meaning",
    sources: "Bible passages and their context",
    footerBible:
      "Scripture quotations from the public-domain World English Bible.",
    selectedVerse: "Selected verse",
    contextOrigin: "Where does this passage come from?",
    broaderContext: "The wider context",
    originalMeaning: "What did it originally mean?",
    application: "How does it relate to your situation?",
    passageContext: "Read the complete unit",
    contextSources: "Context based on these sources",
    footerPrivacy:
      "Your situation is stored only when you explicitly create a share link.",
    analyticsText:
      "Do you agree to anonymous analytics that helps us improve the application? We never send the content of your questions.",
    analyticsAccept: "Accept",
    analyticsReject: "No, thanks",
    question: "Your question",
    sharedQuestion: "Shared question",
    share: "Share",
    sharing: "Creating link…",
    shared: "Link copied",
    ready: "Link is ready",
    sharePrivacy: "Anyone with the link can see this question and response.",
    sharedBadge: "Shared response",
  },
} as const;

export type LocalizedCopy = (typeof localizedCopy)[Language];

export function copyFor(language: Language): LocalizedCopy {
  return localizedCopy[language];
}

export function languageFrom(value: string): Language {
  return value === Language.English ? Language.English : Language.Polish;
}
