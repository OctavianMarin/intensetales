from flask import request, session
from random import choice


class Text:
    supported_langs = [
        'english',
        'italiano'
    ]

    def __init__(self):
        if request.args.get('lang') is not None:
            session['lang'] = request.args.get('lang')
        if 'lang' in session:
            self.lang = session['lang']
        else:
            self.lang = 'english'

    def title(self, name, title=''):
        names = {
            'signup': {
                'english': "Sign Up",
                'italiano': "Iscriviti"
            },
            'validation': {
                'english': "Validation",
                'italiano': "Validazione"
            },
            'validation_code': {
                'english': "Validation code",
                'italiano': "Codice di validazione"
            },
            'signin': {
                'english': "Sign in",
                'italiano': "Accedi"
            },
            'account': {
                'english': "Account",
                'italiano': "Account"
            },
            'reset_password': {
                'english': "Reset password",
                'italiano': "Reimposta password"
            },
            'publish_story': {
                'english': "Publish a story",
                'italiano': "Pubblica una storia"
            },
            'revisions': {
                'english': f"{title} - revisions",
                'italiano': f"{title} - revisioni"
            },
            'edit': {
                'english': f"{title} - edit",
                'italiano': f"{title} - modifica",
            },
            'banned': {
                'english': "You are banned",
                'italiano': "Sei bannato"
            }
        }
        return names[name][self.lang]

    def description(self, name):
        names = {
            'home': {
                'english': "Read and post short stories. Immerse yourself in the tense atmospheres",
                'italiano': "Leggi e pubblica brevi storie. Immergiti nelle atmosfere di tensione"
            },
            'signup': {
                'english': "Just enter a few simple information to create your account and "
                           "be able to interact more with your favorite creators!",
                'italiano': "Basta inserire poche semplici informazioni per creare il tuo account"
                            " e poter interagire maggiormente con i tuoi creatori preferiti!"
            },
            'validation': {
                'english': "This is your first time logging in from this device. "
                           "Please enter the code that was sent to",
                'italiano': "È la prima volta che accedi da questo dispositivo. "
                            "Per favore inserisci il codice che ti è stato inviato a"
            },
            'signin': {
                'english': "If you already have your account, enter your credentials "
                           "here to resume your activity on the site",
                'italiano': "Se hai già il tuo account, inserisci qui le credenziali "
                            "per riprendere la tua attività sul sito"
            },
            'account': {
                'english': "Here you can manage your account and see all the "
                           "information saved on this site related to your account",
                'italiano': "Qua puoi gestire il tuo account e vedere tutte le informazioni "
                            "salvate su questo sito relative al tuo account"
            },
            'reset_password': {
                'english': "Enter the email you used to create your account. ",
                'italiano': "Inserisci la mail che hai usato per creare il tuo account. "
            },
            'become_creator': {
                'english': "Happy to see that you have chosen to publish "
                           "your content on this platform!",
                'italiano': "Felici di vedere che hai scelto di pubblicare "
                            "i tuoi contenuti su questa piattaforma!"
            },
            'publish_story': {
                'english': "Fill out this page and publish your story!",
                'italiano': "Compila questa pagina e pubblica la tua storia!"
            },
            'revisions': {
                'english': "Check out all the reviews posted so far!",
                'italiano': "Guarda tutte le revisioni pubblicate fin'ora!"
            },
            'edit': {
                'english': "Edit your story attributes here",
                'italiano': "Modifica qui gli attributi della tua storia"
            },
            'banned': {
                'english': "You have negatively impacted the perception of this site. "
                           "Please spend your time elsewhere",
                'italiano': "Hai impattato negativamente la percezione di questo sito. "
                            "Sei pregato di passare il tuo tempo da un'altra parte"
            }
        }
        return names[name][self.lang]

    def input(self, name):
        names = {
            'submit': {
                'english': 'Submit',
                'italiano': 'Invia'
            },
            'resend': {
                'english': "Resend",
                'italiano': "Reinvia"
            },
            'accept': {
                'english': "Accept",
                'italiano': "Accetta"
            },
            'close': {
                'english': "Close",
                'italiano': "Chiudi"
            },
            'actions': {
                'english': "Account actions",
                'italiano': "Azioni sull'account"
            },
            'signout': {
                'english': "Sign out",
                'italiano': "Esci"
            },
            'delete_account': {
                'english': "Delete account",
                'italiano': "Elimina account"
            },
            'change_email': {
                'english': "Change email",
                'italiano': "Modifica email"
            },
            'change_password': {
                'english': "Change password",
                'italiano': "Modifica password"
            },
            'download_data': {
                'english': "Download your data (json)",
                'italiano': "Scarica i tuoi dati (json)"
            },
            'become_creator': {
                'english': "Ready to be a creator!",
                'italiano': "Pronto per diventare creator!"
            },
            'publish_story': {
                'english': "Publish a story",
                'italiano': "Pubblica una storia"
            },
            'story_file': {
                'english': "Select the file where you wrote the story. It must be in txt format",
                'italiano': "Seleziona il file dove hai scritto la storia. Deve essere in formato txt"
            },
            'title': {
                'english': "title",
                'italiano': "titolo"
            },
            'description': {
                'english': "description",
                'italiano': "descrizione"
            },
            'genre': {
                'english': "List the genres of your short story. "
                           "Use only spaces to separate one genre from another",
                'italiano': "Elenca i generi del tuo racconto. "
                            "Usa solo spazi per separare un genere dall'altro"
            },
            'publish_date': {
                'english': "Decide the date on which the story will be visible",
                'italiano': "Decidi la data in cui sarà visibile la storia"
            },
            'image_file': {
                'english': "Select an image for your story",
                'italiano': "Seleziona un'immagine per la tua storia"
            },
            'story_lang': {
                'english': "Specify the language in which you wrote the story",
                'italiano': "Specifica la lingua nella quale hai scritto il racconto"
            },
            'mention': {
                'english': "You can mention collaborators and inspirations in one sentence (not requireds)",
                'italiano': "Puoi menzionare in una frasetta collaboratori e ispirazioni (non obbligatorio)"
            },
            'upload_new_revision': {
                'english': "Upload new revision",
                'italiano': "Carica una nuova revisione"
            },
            'change_title': {
                'english': "Change title",
                'italiano': "Modifica titolo"
            },
            'change_description': {
                'english': "Change description",
                'italiano': "Modifica descrizione"
            },
            'change_mention': {
                'english': "Change mention",
                'italiano': "Modifica menzione"
            },
            'change_lang': {
                'english': "Change language",
                'italiano': "Modifica lingua"
            },
            'change_publish_date': {
                'english': "Change visibility date",
                'italiano': "Modifica la data in cui sarà visibile"
            },
            'change_genres': {
                'english': "Change genres",
                'italiano': "Modifica i generi"
            },
            'change_image_file': {
                'english': "Change the image",
                'italiano': "Modifica l'immagine"
            },
            'write_comment': {
                'english': "Write a comment",
                'italiano': "Scrivi un commento"
            },
            'delete_story': {
                'english': "Delete story",
                'italiano': "Elimina storia"
            },
            'see_original': {
                'english': "See the original",
                'italiano': "Vedi l'originale"
            },
            'see_translation': {
                'english': "See the translation",
                'italiano': "Vedi la traduzione"
            }
        }
        return names[name][self.lang]

    def descriptor(self, name):
        names = {
            'username': {
                'english': "Username",
                'italiano': "Username"
            },
            'email': {
                'english': "Email",
                'italiano': "Email"
            },
            'devices': {
                'english': "Your devices",
                'italiano': "I tuoi dispositivi"
            }
        }
        return names[name][self.lang]

    def error(self, name):
        names = {
            'username_len': {
                'english': "The username's length must be at least 3 characters",
                'italiano': "La lunghezza dell'username deve essere di almeno 3 caratteri"
            },
            '@_username': {
                'english': "The username cannot contain '@' character",
                'italiano': "L'username non può contenere il carattere '@'"
            },
            'password_len': {
                'english': "The password's length must be at least 4 characters",
                'italiano': "La lunghezza della tua password deve essere di almeno 4 caratteri"
            },
            'username_used': {
                'english': "This username is already used",
                'italiano': "Questo username è già in uso"
            },
            'different_passwords': {
                'english': "You have to repeat the same password twice. You inserted 2 different passwords",
                'italiano': "Devi ripetere la stessa password 2 volte. Hai inserito 2 password diverse"
            },
            'wrong_id': {
                'english': "Attention! You have entered an incorrect code",
                'italiano': "Attenzione! Hai inserito un codice errato"
            },
            'no_user': {
                'english': "This username does not exist. If you want to create it go to the registration page",
                'italiano': "Questo username non esiste. Se vuoi crearlo vai nella pagina di registrazione"
            },
            'no_email': {
                'english': "This mail is not related to any account. "
                           "If you want to create an account go to the registration page",
                'italiano': "Questa mail non è correllata a nessun account. "
                            "Se vuoi creare un account vai sulla pagina di registrazione"
            },
            'wrong_password': {
                'english': "The entered password is incorrect",
                'italiano': "La password inserita è errata"
            },
            'no_creator_user': {
                'english': "There is no user with this username",
                'italiano': "Non esiste nessun user con questo username"
            },
            'no_creator': {
                'english': "This user is not a creator",
                'italiano': "Questo utente non è un creator"
            },
            'not_your_account': {
                'english': "You can only post stories to your creator page",
                'italiano': "Puoi pubblicare storie solo sulla tua pagina creator"
            },
            'no_title': {
                'english': "You need to decide on a title for your short story",
                'italiano': "Devi decidere un titolo per il tuo racconto"
            },
            'description_len': {
                'english': "The length of the description must be at least 64 characters",
                'italiano': "La lunghezza della descrizione deve essere di almeno 64 caratteri"
            },
            'no_story_file': {
                'english': "You must attach the file with your story",
                'italiano': "Devi allegare il file con la tua storia"
            },
            'invalid_lang': {
                'english': "You must select a language from those supported",
                'italiano': "Devi selezionare una lingua tra quelle supportate"
            },
            'title_already_exist': {
                'english': "There is already a story with this title",
                'italiano': "Esiste già una storia con questo titolo"
            },
            'cannot_load_image': {
                'english': "Your image cannot be processed",
                'italiano': "Non si riesce a processare la tua immagine"
            },
            'no_genre': {
                'english': "Specify the genres to which your story is related",
                'italiano': "Specifica i generi a cui è riconducibile il tuo racconto"
            },
            'past_date': {
                'english': "Your story's publication date cannot be before tomorrow",
                'italiano': "La data di pubblicazione della tua storia non può precedere domani"
            }
        }
        return names[name][self.lang]

    def mail(self, name):
        names = {
            'validation': {
                'english': "We are happy to see that you have decided to spend some time on our site!"
                           " Prove that you are accessing by entering the following code in the dedicated form ",
                'italiano': "Siamo contenti di vedere che hai deciso di dedicare del tempo "
                            "sul nostro sito! Dimostra di essere tu ad accedere inserendo il seguente "
                            "codice nell'apposito form "
            },
            'reset_password': {
                'english': "Prove that you are trying to reset your account password "
                           "by entering the following code in the appropriate form ",
                'italiano': "Dimostra di essere tu che stai cercando di reimpostare la password del "
                            "tuo account inserendo il seguente codice nell'apposito form "
            }
        }
        return names[name][self.lang]

    def advice(self, name, revisions=''):
        names = {
            'already_account': {
                'english': "Do you already have an account? If yes, then you must go here",
                'italiano': "Hai già un account? Se si, allora devi andare qui"
            },
            'reset_password': {
                'english': "Did you forget your password? come here",
                'italiano': "Hai dimenticato la password? Vieni qua"
            },
            'become_creator': {
                'english': "Want to start writing content? Come to this page",
                'italiano': "Vuoi iniziare a scrivere contenuti? Vieni su questa pagina"
            },
            'creator_page': {
                'english': "Maybe you want to manage your creations. If so, come here",
                'italiano': "Forse vuoi gestire le tue creazioni. Se è così, vieni qua"
            },
            'revisions_history': {
                'english': f"{revisions} revisions have been done so far. You can see all the revision history here",
                'italiano': f"Sono state fatte {revisions} revisioni finora. Puoi vedere tutta la storia delle revisioni qui"
            },
            'manage_content': {
                'english': "To manage the content of your story go here",
                'italiano': "Per gestire il contenuto della tua storia vai qui"
            },
            'translated_by': {
                'english': "Translated by",
                'italiano': "Tradotto con"
            }
        }
        return names[name][self.lang]

    def popup(self, name):
        names = {
            'cookies': {
                'english': "We want to inform you that we use cookies in order to recognize you "
                           "when you enter our site and also to monitor "
                           "the flow of users arriving on our site",
                'italiano': "Vogliamo informarti che usiamo cookie al fine di riconescerti "
                            "quando entri sul nostro sito e anche per monitorare "
                            "il flusso di utenti che arriva sul nostro sito"
            },
            'choose_lang': {
                'english': "Choose the language in which you want to view the contents of this site",
                'italiano': "Scegli la lingua nella quale vuoi visualizzare i contenuti di questo sito"
            },
            'insert_code': {
                'english': "Enter the code you received by mail and the new password you want to create",
                'italiano': "Inserisci il codice che ti è arrivato per mail e la nuova password che vuoi creare"
            },
            'changes': {
                'english': "Careful! You are about to make the changes listed here. "
                           "If you are sure, confirm with your password",
                'italiano': "Attento! Stai per apportare le modifiche elencate qua. "
                            "Se sei sicuro conferma con la tua password"
            }
        }
        return names[name][self.lang]

    def citation(self):
        citations = [
            [
                {
                    'english': "The future of science fiction? We live in it. […] "
                               "If there's one thing I've learned from science fiction, "
                               "it's that every present moment is simultaneously someone "
                               "else's past and someone else's future.",
                    'italiano': "Il futuro della fantascienza? Ci viviamo dentro. […] "
                                "Se c'è una cosa che ho imparato dalla fantascienza, "
                                "è che ogni momento presente è al contempo il passato "
                                "di qualcun altro e il futuro di qualcun altro."
                },
                "William Gibson"
            ],
            [
                {
                    'english': "The only advice one person can give to another about reading is not to take advice, "
                               "to follow your instincts, to use your own head, to come to your own conclusions.",
                    'italiano': "L’unico consiglio che una persona può dare a un’altra sulla lettura "
                                 "è di non accettare consigli, di seguire il proprio istinto, "
                                 "di usare la propria testa, di arrivare alle proprie conclusioni."
                },
                "Virginia Woolf"
            ],
            [
                {
                    'english': "How many men have dated the beginning of a new era "
                               "in their life by reading a book.",
                    'italiano': "Quanti uomini hanno datato l'inizio di una nuova "
                                 "era della loro vita dalla lettura di un libro."
                },
                "Henry David Thoreau"
            ],
            [
                {
                    'english': "The best way to read books is to follow the law of pleasure...",
                    'italiano': "Il miglior metodo per la lettura dei libri "
                                "è quello di seguir la legge del piacere..."
                },
                "Cesare Beccaria"
            ],
            [
                {
                    'english': "Life is a perennial obstacle to reading.",
                    'italiano': "La vita è un perenne ostacolo alla lettura."
                },
                "Daniel Pennac"
            ],
            [
                {
                    'english': "A writer needs to know how people read, "
                               "what are the main sources of reading errors, "
                               "and what can be done to prevent them.",
                    'italiano': "Uno scrittore deve sapere come leggono le persone, "
                                "quali sono le principali fonti di errori di lettura "
                                "e cosa si può fare per prevenirli."
                },
                "Rudolph Flesch"
            ],
            [
                {
                    'english': "Ask a science fiction writer and he'll come up with something. "
                               "Soon someone else will want to put it into practice.",
                    'italiano': "Chiedi a uno scrittore di fantascienza e s'inventerà qualcosa. "
                                "Poco dopo qualcun altro vorrà metterlo in pratica."
                },
                "Margaret Atwood"
            ],
            [
                {
                    'english': "You can say this about me: I'm a science fiction writer, "
                               "a horror writer and a writer full stop. I'm addressing three audiences "
                               "who will never meet, yet I've tried to introduce them to each other "
                               "to at least shake hands.",
                    'italiano': "Di me si può dire questo: sono uno scrittore di fantascienza, "
                                "uno scrittore dell'orrore e uno scrittore punto e basta. "
                                "Mi rivolgo a tre tipi di pubblico che non s'incontreranno mai, "
                                "e tuttavia ho cercato di presentarli l'uno all'altro perché "
                                "si scambiassero almeno una stretta di mano."
                },
                "Dan Simmons"
            ],
            [
                {
                    'english': "A good reader is as rare as a good writer.",
                    'italiano': "Un buon lettore è raro quanto un bravo scrittore."
                },
                "Jorge Luis Borges"
            ]
        ]
        cit = choice(citations)
        return cit[0][self.lang], cit[1]
