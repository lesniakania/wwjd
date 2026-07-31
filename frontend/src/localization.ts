export enum Language {
  Polish = "pl",
  English = "en",
}

const localizedCopy = {
  [Language.Polish]: {
    appTitle: "Co na to Jezus?",
    homeLabel: "Co na to Jezus? — strona główna",
    header: "Refleksja oparta na Biblii",
    eyebrow: "Chwila na zatrzymanie",
    title1: "Co na to",
    title2: "Jezus?",
    intro:
      "Opisz, z czym się mierzysz. Odszukamy odpowiednie fragmenty Pisma i zaproponujemy przemyślaną, praktyczną refleksję opartą na Biblii.",
    label: "Co na to Jezus?",
    placeholder: "Zmagam się z trudną decyzją w pracy…",
    privacy: "Opisz sytuację bez prywatnych danych innych osób.",
    submit: "Znajdź drogę naprzód",
    loading: "Szukam odpowiedzi…",
    tipsTitle:
      "Jaśniejszy opis sytuacji pozwala stworzyć bardziej pomocną refleksję",
    tips: [
      "Najpierw opisz fakty, a potem własną interpretację.",
      "Staraj się unikać oceniających określeń i osądów.",
      "Pomiń imiona, adresy i dane pozwalające zidentyfikować osoby.",
    ],
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
    contextSources: "Kontekst zweryfikowany przez człowieka na podstawie tych źródeł",
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
    eyebrow: "A moment to pause",
    title1: "What would",
    title2: "Jesus do?",
    intro:
      "Describe what you are facing. We’ll look for relevant Scripture and offer a thoughtful, practical reflection based on the Bible.",
    label: "What would Jesus do?",
    placeholder: "I’m struggling with a decision at work...",
    privacy: "Share the situation, not anyone’s private details.",
    submit: "Find a way forward",
    loading: "Reflecting…",
    tipsTitle: "A clearer situation leads to a more useful reflection",
    tips: [
      "Describe the facts before your interpretation of them.",
      "Try to avoid judgmental language and assumptions.",
      "Leave out names, addresses, and identifying details.",
    ],
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
    contextSources: "Human-reviewed context based on these sources",
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
