# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import random
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from google.adk.tools import ToolContext
from google.genai import types

def clean_html(html_content: str) -> str:
    # Remove script and style tags
    content = re.sub(r'<(script|style)\b[^>]*>([\s\S]*?)</\1>', '', html_content)
    # Remove comments
    content = re.sub(r'<!--([\s\S]*?)-->', '', content)
    # Replace tags with spaces
    content = re.sub(r'<[^>]+>', ' ', content)
    # Compress whitespace
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def search_documentation(query: str) -> dict:
    """Recherche dans le site web officiel et les documents de la mairie de Brignon-les-Bains.
    Utilisez cet outil pour répondre aux questions sur les horaires, les démarches,
    l'actualité ou l'histoire de la commune.

    Args:
        query: Les mots-clés ou la question de recherche.

    Returns:
        Un dictionnaire contenant les pages correspondantes et leur contenu textuel.
    """
    workspace_dir = "/Users/benjaminpolge/Downloads/Brignon-les-Bains"
    results = {}
    
    # Extract keywords of length >= 4
    keywords = [w.lower() for w in re.findall(r'\b\w{4,}\b', query) if w.lower() not in ["pour", "dans", "avec", "mairie"]]
    if not keywords:
        keywords = [query.lower()]
        
    for filename in os.listdir(workspace_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(workspace_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
                title = title_match.group(1) if title_match else filename
                
                clean_text = clean_html(html_content)
                
                # Simple keyword score
                score = sum(1 for kw in keywords if kw in clean_text.lower())
                
                # Also check filename match
                if score > 0 or any(kw in filename.lower() for kw in keywords):
                    results[filename] = {
                        "title": title,
                        "content": clean_text[:2500]  # Limit context size
                    }
            except Exception:
                pass
                
    if not results:
        return {"message": "Aucun document correspondant n'a été trouvé sur le site de la mairie."}
    return results

def classify_request(query: str) -> dict:
    """Classifie la demande de l'usager parmi les thématiques municipales de Brignon-les-Bains.

    Args:
        query: Le message ou la demande de l'usager.

    Returns:
        Un dictionnaire contenant la catégorie identifiée et le niveau de confiance.
    """
    q = query.lower()
    
    mapping = {
        "état civil": ["acte", "naissance", "mariage", "décès", "pacs", "livret de famille", "cni", "carte d'identité", "passeport", "identité", "certificat"],
        "inscription scolaire ou périscolaire": ["école", "scolaire", "inscription école", "périscolaire", "cantine", "garderie", "enfant", "élève"],
        "prise de rendez-vous avec un service municipal": ["rendez-vous", "rdv", "rencontrer", "voir un agent", "permanence", "rdv mairie"],
        "réservation de salle ou d’équipement public": ["réserver salle", "réservation salle", "salle municipale", "fêtes", "équipement", "louer salle"],
        "signalement de problème de voirie": ["nid-de-poule", "lampadaire", "panne", "dépôt sauvage", "arbre tombé", "trottoir", "mobilier urbain", "propreté", "danger", "voirie", "trou", "dégradé", "fuite"],
        "stationnement": ["parking", "stationner", "place de parc", "amende", "zone bleue", "stationnement"],
        "propreté": ["poubelle", "ordures", "propreté", "balayage", "détritus", "dépôt sauvage"],
        "urbanisme": ["permis de construire", "déclaration de travaux", "urbanisme", "cadastre", "construire", "travaux maison", "plu"],
        "vie associative": ["association", "subvention", "club", "bénévole", "sport", "culture"],
    }
    
    for category, keywords in mapping.items():
        if any(kw in q for kw in keywords):
            return {"category": category, "confidence": "high"}
            
    return {"category": "demande d’information générale", "confidence": "medium"}

def generate_checklist(action_type: str) -> dict:
    """Génère la liste des pièces justificatives et des étapes pour une démarche administrative.

    Args:
        action_type: Le type de démarche ('cni', 'passeport', 'inscription_scolaire', 'mariage', 'urbanisme').

    Returns:
        Un dictionnaire avec les documents requis, les étapes et le coût.
    """
    checklists = {
        "cni": {
            "procedure": "Carte Nationale d'Identité",
            "documents": [
                "Formulaire de pré-demande en ligne (ou Cerfa papier)",
                "Une photo d'identité récente aux normes",
                "Un justificatif de domicile de moins d'un an",
                "L'ancienne carte d'identité (ou déclaration de perte/vol)",
                "Pour les mineurs : autorisation parentale + pièce d'identité du parent"
            ],
            "steps": [
                "Faire la pré-demande sur ants.gouv.fr",
                "Prendre RDV en mairie (équipée d'une station biométrique, Brignon-les-Bains n'en ayant pas, voir les communes limitrophes)",
                "Déposer le dossier en personne pour la prise d'empreintes",
                "Retirer la carte sous 2 à 4 semaines"
            ],
            "cost": "Gratuit (sauf perte/vol : timbre fiscal de 25€)"
        },
        "passeport": {
            "procedure": "Passeport biométrique",
            "documents": [
                "Pré-demande en ligne imprimée",
                "Photo d'identité conforme récente",
                "Justificatif de domicile récent",
                "Ancien passeport (si renouvellement) ou CNI",
                "Timbre fiscal dématérialisé (86€ adulte, 42.50€ mineur de 15+ ans, 17€ mineur de moins de 15 ans)"
            ],
            "steps": [
                "Acheter le timbre fiscal en ligne",
                "Faire la pré-demande sur ants.gouv.fr",
                "Prendre RDV dans une mairie équipée d'une station biométrique",
                "Déposer le dossier et faire la prise d'empreintes",
                "Retirer le passeport sous 2 à 6 semaines"
            ],
            "cost": "Variable selon l'âge (coût du timbre fiscal)"
        },
        "inscription_scolaire": {
            "procedure": "Inscription scolaire",
            "documents": [
                "Livret de famille ou acte de naissance de l'enfant",
                "Justificatif de domicile",
                "Carnet de santé (vaccinations obligatoires à jour, notamment DTP)",
                "Certificat de radiation (si changement d'école)"
            ],
            "steps": [
                "Retirer le dossier au secrétariat de la mairie (ou sur le site internet)",
                "Déposer le dossier complété avec les pièces justificatives",
                "Obtenir le certificat d'inscription délivré par la mairie",
                "Prendre rendez-vous avec la direction de l'école pour valider définitivement l'admission"
            ],
            "cost": "Gratuit"
        },
        "mariage": {
            "procedure": "Mariage civil / PACS",
            "documents": [
                "Pièces d'identité des futurs époux/partenaires",
                "Justificatifs de domicile récents (de moins de 3 mois)",
                "Copies intégrales d'actes de naissance de moins de 3 mois",
                "Fiche de renseignements des témoins (pour mariage)",
                "Convention de PACS et déclaration conjointe (pour PACS)"
            ],
            "steps": [
                "Retirer le dossier d'état civil en mairie de Brignon-les-Bains",
                "Constituer le dossier complet avec toutes les pièces justificatives",
                "Prendre rendez-vous au service état civil pour déposer le dossier conjointement",
                "Publication légale des bans (10 jours obligatoires avant la cérémonie)"
            ],
            "cost": "Gratuit"
        },
        "urbanisme": {
            "procedure": "Déclaration préalable / Permis de construire",
            "documents": [
                "Formulaire Cerfa réglementaire adapté aux travaux",
                "Plan de situation du terrain dans la commune",
                "Plan de masse des constructions à édifier ou modifier",
                "Plan de coupe du terrain et de la construction",
                "Notice décrivant le terrain et le projet",
                "Documents graphiques ou photographies de l'environnement"
            ],
            "steps": [
                "Consulter le Plan Local d'Urbanisme (PLU) en mairie",
                "Prendre rendez-vous avec le service urbanisme (permanences mardi/jeudi matin)",
                "Déposer le dossier complet en mairie (4 exemplaires papier)",
                "Attendre l'instruction (1 mois pour DP, 2-3 mois pour permis de construire)"
            ],
            "cost": "Instruction gratuite"
        }
    }
    return checklists.get(action_type.lower(), {
        "error": f"Démarche '{action_type}' non répertoriée. Veuillez appeler le secrétariat de la mairie au 04 75 62 14 30."
    })

def generate_recap(data: dict) -> str:
    """Génère un récapitulatif structuré en Markdown des informations collectées pour une démarche.

    Args:
        data: Un dictionnaire contenant les informations de l'usager.

    Returns:
        Une chaîne Markdown récapitulative.
    """
    recap = "### Récapitulatif des informations collectées\n\n"
    for key, value in data.items():
        formatted_key = key.replace("_", " ").capitalize()
        recap += f"* **{formatted_key}** : {value}\n"
    return recap

def prepare_appointment(service: str, reason: str, name: str, contact: str, timeslot: str) -> dict:
    """Prépare les détails d'une demande de rendez-vous en mairie de Brignon-les-Bains.

    Args:
        service: Le service concerné (urbanisme, état civil, CCAS, secrétariat).
        reason: Le motif du rendez-vous.
        name: Le nom complet de l'usager.
        contact: Les coordonnées de l'usager (téléphone ou e-mail).
        timeslot: Le créneau horaire souhaité.

    Returns:
        Un dictionnaire contenant les informations du rendez-vous pré-enregistré.
    """
    appt_id = f"RDV-{random.randint(1000, 9999)}"
    
    docs_to_bring = ["Pièce d'identité en cours de validité"]
    s = service.lower()
    if "urban" in s:
        docs_to_bring.extend(["Plans du terrain", "Photos de l'existant", "Formulaire Cerfa pré-rempli"])
    elif "social" in s or "ccas" in s:
        docs_to_bring.extend(["Justificatifs de ressources des 12 derniers mois", "Dernier avis d'imposition", "Justificatif de domicile"])
    elif "civil" in s or "identité" in s:
        docs_to_bring.extend(["Justificatif de domicile récent (moins de 3 mois)", "Photos d'identité conformes", "Livret de famille"])
        
    return {
        "appointment_id": appt_id,
        "service": service,
        "reason": reason,
        "citizen_name": name,
        "contact_info": contact,
        "timeslot": timeslot,
        "status": "Pré-enregistré (en attente de confirmation finale par les agents)",
        "documents_to_bring": docs_to_bring,
        "message": f"Votre demande de rendez-vous a été pré-enregistrée avec la référence {appt_id}."
    }

def prepare_room_booking(date: str, hours: str, people_count: int, event_type: str, room_name: str, special_needs: str) -> dict:
    """Prépare une demande de réservation de salle ou d'équipement communal.

    Args:
        date: La date souhaitée (format AAAA-MM-DD).
        hours: Les heures d'occupation (ex: 14h-18h).
        people_count: Le nombre de personnes prévues.
        event_type: Le type d'événement (réunion, fête, AG, etc.).
        room_name: Le nom de la salle demandée (Salle des Fêtes, Salle du Conseil, Foyer Municipal).
        special_needs: Besoins particuliers (sono, tables, chaises, cuisine).

    Returns:
        Un dictionnaire résumant la demande de réservation.
    """
    booking_id = f"RES-{random.randint(1000, 9999)}"
    
    rooms = {
        "Salle des Fêtes": {"capacity": 150, "facilities": "Cuisine équipée, tables, chaises, sonorisation"},
        "Salle du Conseil": {"capacity": 30, "facilities": "Vidéoprojecteur, tables de réunion, chaises"},
        "Foyer Municipal": {"capacity": 60, "facilities": "Tables, chaises, bar avec évier"}
    }
    
    room_info = rooms.get(room_name, {"capacity": 50, "facilities": "Tables, chaises"})
    
    status = "Soumis à validation par le service Vie Associative"
    warning = ""
    if people_count > room_info["capacity"]:
        status = "Refusé (Capacité maximale dépassée)"
        warning = f"La capacité maximale de la salle '{room_name}' est de {room_info['capacity']} personnes. Votre demande concerne {people_count} personnes."
        
    return {
        "booking_id": booking_id,
        "room_name": room_name,
        "date": date,
        "hours": hours,
        "people_count": people_count,
        "event_type": event_type,
        "special_needs": special_needs,
        "status": status,
        "warning": warning,
        "facilities_available": room_info["facilities"],
        "message": f"Votre demande de réservation a été pré-enregistrée sous la référence {booking_id}."
    }

def create_report_ticket(problem_type: str, address: str, urgency: str, description: str, danger: bool) -> dict:
    """Crée un ticket de signalement d'anomalie dans l'espace public (voirie, éclairage, propreté, etc.).

    Args:
        problem_type: Type de problème (nid-de-poule, lampadaire en panne, dépôt sauvage, arbre tombé, trottoir, mobilier dégradé).
        address: L'adresse précise de l'incident.
        urgency: Le niveau d'urgence suggéré ('faible', 'moyen', 'fort', 'critique').
        description: Description détaillée du problème.
        danger: Indique s'il y a un danger immédiat pour la sécurité des usagers (True/False).

    Returns:
        Un dictionnaire décrivant le ticket de signalement créé.
    """
    ticket_id = f"SIG-{random.randint(100000, 999999)}"
    
    dept_mapping = {
        "nid-de-poule": "Services Techniques - Voirie",
        "lampadaire en panne": "Services Techniques - Électricité",
        "dépôt sauvage": "Service Propreté & Environnement",
        "arbre tombé": "Service Espaces Verts / Protection Civile",
        "arbre dangereux": "Service Espaces Verts",
        "trottoir impraticable": "Services Techniques - Voirie",
        "mobilier urbain dégradé": "Services Techniques - Aménagement Urbain",
        "problème de propreté": "Service Propreté & Environnement",
        "danger pour les piétons": "Police Municipale / Services Techniques",
        "danger pour les cyclistes": "Police Municipale / Services Techniques",
    }
    
    department = "Services Techniques"
    for k, v in dept_mapping.items():
        if k in problem_type.lower():
            department = v
            break
            
    final_urgency = urgency
    if danger:
        final_urgency = "critique"
        
    return {
        "ticket_id": ticket_id,
        "problem_type": problem_type,
        "address": address,
        "urgency_level": final_urgency,
        "recipient_department": department,
        "synthesis": f"SIGNALEMENT USAGER [{ticket_id}] - Type : {problem_type} | Adresse : {address}. Urgence : {final_urgency}. Danger : {'OUI' if danger else 'NON'}. Description : {description}",
        "receipt": {
            "title": "Récépissé de signalement de voirie",
            "message": f"Votre signalement a été enregistré avec succès sous le numéro {ticket_id}. Le service municipal concerné ({department}) a été immédiatement saisi de votre demande.",
            "next_steps": "Les agents municipaux vont procéder à une vérification technique sur site pour planifier l'intervention. Merci pour votre signalement."
        }
    }

def create_pdf_bytes(title: str, service: str, user_name: str, obj: str, body: str, next_steps: str, date_str: str, dossier_id: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter # 612, 792
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.06, 0.3, 0.36) # Mairie primary color #0f4c5c
    c.drawString(50, 730, "MAIRIE DE BRIGNON-LES-BAINS (Ardèche)")
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.36, 0.42, 0.45) # text light
    c.drawString(50, 715, f"Date : {date_str}  |  Dossier N° : {dossier_id}")
    
    c.setStrokeColorRGB(0.88, 0.86, 0.83) # border color #e0dcd3
    c.setLineWidth(1)
    c.line(50, 705, width - 50, 705)
    
    # Document Title
    c.setFont("Helvetica-Bold", 13)
    c.setFillColorRGB(0.04, 0.21, 0.25) # dark primary
    c.drawString(50, 680, title.upper())
    
    # Meta fields
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.13, 0.2, 0.23) # text dark
    c.drawString(50, 655, "SERVICE : ")
    c.setFont("Helvetica", 10)
    c.drawString(110, 655, service)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 640, "CONCERNANT : ")
    c.setFont("Helvetica", 10)
    c.drawString(140, 640, user_name)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 625, "OBJET : ")
    c.setFont("Helvetica", 10)
    c.drawString(110, 625, obj)
    
    c.line(50, 615, width - 50, 615)
    
    # Body text (draw line by line, handle wrapping)
    y = 590
    c.setFont("Helvetica", 10.5)
    c.setFillColorRGB(0.13, 0.2, 0.23)
    for line in body.split('\n'):
        words = line.split(' ')
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, "Helvetica", 10.5) < (width - 100):
                current_line = test_line
            else:
                c.drawString(50, y, current_line)
                y -= 15
                current_line = word
                if y < 150: # Page break
                    c.showPage()
                    y = 720
                    c.setFont("Helvetica", 10.5)
        if current_line:
            c.drawString(50, y, current_line)
            y -= 18
            
    c.line(50, y, width - 50, y)
    
    # Next steps
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "PROCHAINES ÉTAPES :")
    c.setFont("Helvetica", 10)
    c.drawString(180, y, next_steps)
    
    # Footer Disclaimer
    c.setStrokeColorRGB(0.92, 0.7, 0.3) # gold border #e9b44c
    c.setFillColorRGB(0.98, 0.96, 0.94) # gold bg
    c.rect(50, 50, width - 100, 45, fill=True, stroke=True)
    
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColorRGB(0.06, 0.3, 0.36)
    c.drawCentredString(width / 2, 76, "MENTION LÉGALE : Document fictif généré dans le cadre d'une démonstration")
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(width / 2, 62, "— SANS VALEUR ADMINISTRATIVE OU JURIDIQUE —")
    
    c.showPage()
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

async def generate_administrative_document(doc_type: str, user_name: str, details: dict, tool_context: ToolContext = None) -> str:
    """Génère un document administratif officiel fictif de démonstration pour Brignon-les-Bains et crée un PDF téléchargeable.

    Args:
        doc_type: Type de document ('convocation_rdv', 'confirmation_depot', 'autorisation_salle', 'arrete_municipal', 'recepisse_signalement', 'attestation_activite', 'reponse_administrative', 'transmission_interne', 'courrier_officiel').
        user_name: Nom complet de l'usager concerné.
        details: Dictionnaire contenant les paramètres variables du document.
        tool_context: Contexte de l'outil pour enregistrer le fichier généré.

    Returns:
        Une chaîne contenant le document mis en forme avec un lien de téléchargement PDF.
    """
    today = datetime.date.today().strftime("%d/%m/%Y")
    dossier_id = f"F-2026-{random.randint(10000, 99999)}"
    
    doc = "=" * 80 + "\n"
    doc += "                MAIRIE DE BRIGNON-LES-BAINS (Ardèche)\n"
    doc += f"                Date de délivrance : {today} | N° Dossier : {dossier_id}\n"
    doc += "=" * 80 + "\n\n"
    
    doc_types = {
        "convocation_rdv": {
            "title": "CONVOCATION À UN RENDEZ-VOUS EN MAIRIE",
            "service": "Secrétariat Général / Service d'Accueil",
            "object": "Examen et dépôt d'un dossier administratif",
            "body": f"Vous êtes convoqué(e) en mairie de Brignon-les-Bains le {details.get('timeslot', 'prochainement')} pour un entretien avec le service {details.get('service', 'concerné')}.\nMotif : {details.get('reason', 'Constitution de dossier')}.\n\nMerci de vous munir de votre pièce d'identité et des justificatifs nécessaires.",
            "next": "Présentez-vous à l'accueil de la mairie 5 minutes avant l'heure indiquée."
        },
        "confirmation_depot": {
            "title": "CONFIRMATION DE DÉPÔT DE DEMANDE",
            "service": "Service des Affaires Administratives",
            "object": f"Réception de votre dossier de {details.get('procedure', 'demande')}",
            "body": f"La mairie de Brignon-les-Bains atteste de la bonne réception du dossier complet concernant la démarche '{details.get('procedure', 'Demande générale')}' initiée par {user_name}.\nTous les justificatifs obligatoires ont été validés.",
            "next": f"Votre demande est en cours d'instruction par nos agents municipaux. Le délai de réponse est estimé à {details.get('delay', '15 jours')}."
        },
        "autorisation_salle": {
            "title": "AUTORISATION DE RÉSERVATION DE SALLE COMMUNALE",
            "service": "Service d'Aménagement et Vie Associative",
            "object": f"Mise à disposition temporaire de la salle : '{details.get('room_name', 'Salle des Fêtes')}'",
            "body": f"Le Maire de Brignon-les-Bains autorise {user_name} à occuper la salle '{details.get('room_name', 'Salle des Fêtes')}' le {details.get('date', 'date réservée')} de {details.get('hours', 'horaires')} pour l'événement suivant : {details.get('event_type', 'Réunion/Fête/AG')}.\nCapacité d'accueil maximale autorisée : {details.get('people_count', 'non spécifié')} personnes.",
            "next": "Les clés sont à retirer au secrétariat de la mairie le jour ouvrable précédent l'événement, contre dépôt d'un chèque de caution."
        },
        "arrete_municipal": {
            "title": "ARRÊTÉ MUNICIPAL FICTIF SIMPLIFIÉ",
            "service": "Secrétariat Général du Maire",
            "object": f"Réglementation de voirie et de police municipale : {details.get('subject', 'mesure de sécurité')}",
            "body": f"Le Maire de Brignon-les-Bains,\nVU le Code général des collectivités territoriales,\nCONSIDÉRANT la nécessité d'assurer la sécurité et le bon ordre public :\nARRÊTE :\nArticle 1er: {details.get('decision', 'La circulation est réglementée aux abords de la place centrale')}.\nArticle 2: Ces dispositions entrent en vigueur à compter du {today}.",
            "next": "Cet arrêté fera l'objet d'un affichage officiel aux panneaux de la mairie."
        },
        "recepisse_signalement": {
            "title": "RÉCÉPISSÉ DE SIGNALEMENT D'ANOMALIE DE VOIRIE",
            "service": "Services Techniques Municipaux",
            "object": f"Signalement citoyen enregistré - Réf : {details.get('ticket_id', 'SIG-XXXXXX')}",
            "body": f"Nous accusons réception officielle du signalement effectué par {user_name} :\n- Type d'incident : {details.get('problem_type', 'Anomalie sur la voie publique')}\n- Localisation : {details.get('address', 'non spécifiée')}\n- Niveau d'urgence : {details.get('urgency_level', 'Moyen')}\n- Détails : {details.get('description', 'aucune description supplémentaire')}.",
            "next": f"Le ticket a été transmis au service '{details.get('recipient_department', 'Services Techniques')}' pour intervention sur site."
        },
        "attestation_activite": {
            "title": "ATTESTATION FICTIVE D'INSCRIPTION À UNE ACTIVITÉ MUNICIPALE",
            "service": "Service Vie Scolaire & Périscolaire",
            "object": f"Inscription à l'activité municipale '{details.get('activity', 'Périscolaire / Sport / Culture')}'",
            "body": f"La mairie de Brignon-les-Bains atteste que {user_name} (ou son enfant à charge) est officiellement inscrit(e) à l'activité municipale '{details.get('activity', 'Activité communale')}' pour la période en cours.\nStatut de l'inscription : Dossier complet et validé.",
            "next": "Veuillez vous présenter à la première séance de l'activité muni de cette attestation imprimée."
        },
        "reponse_administrative": {
            "title": "RÉPONSE ADMINISTRATIVE OFFICIELLE FICTIVE",
            "service": "Cabinet du Maire",
            "object": f"Réponse à votre courrier concernant {details.get('subject', 'votre demande')}",
            "body": f"Madame, Monsieur {user_name},\nEn réponse à votre sollicitation concernant '{details.get('subject', 'votre dossier')}', nos services ont étudié attentivement votre situation.\nDécision : {details.get('decision', 'Votre dossier est accepté sous réserve de vérification finale.')}.",
            "next": "Aucune action supplémentaire n'est requise de votre part pour le moment."
        },
        "transmission_interne": {
            "title": "FICHE DE TRANSMISSION INTERNE AUX SERVICES",
            "service": "Direction Générale des Services (DGS)",
            "object": f"Note de transmission interne - Dossier de l'usager {user_name}",
            "body": f"DE : Accueil / Assistant Municipal IA\nÀ : Service municipal concerné : {details.get('target_service', 'Services Techniques')}\nContenu du dossier : {details.get('summary', 'Fiche de demande transmise pour instruction interne.')}.",
            "next": "Le service destinataire dispose de 48h pour accuser réception de cette note interne."
        },
        "courrier_officiel": {
            "title": "COURRIER OFFICIEL DE LA MAIRIE",
            "service": "Cabinet du Maire de Brignon-les-Bains",
            "object": f"Courrier officiel adressé à {user_name}",
            "body": f"Madame, Monsieur {user_name},\n\nNous faisons suite à votre demande et tenons à vous informer des éléments suivants :\n{details.get('content', 'Nos services ont bien pris note de votre démarche et y apporteront la plus grande attention.')}\n\nRestant à votre entière disposition pour tout complément d'information,\n\nCordialement,\nLe Maire de Brignon-les-Bains",
            "next": "Pour toute correspondance ultérieure, veuillez rappeler la référence de dossier figurant en en-tête."
        },
        "acte_naissance": {
            "title": "COPIE INTÉGRALE D'ACTE DE NAISSANCE (FICTIF)",
            "service": "Service de l'État Civil / Mairie de Brignon-les-Bains",
            "object": f"Extrait d'acte de naissance pour {user_name}",
            "body": f"EXTRAIT DU REGISTRE DES ACTES DE NAISSANCE DE LA COMMUNE DE BRIGNON-LES-BAINS\n\nNom de famille : {details.get('lastname', 'Non renseigné')}\nPrénoms : {details.get('firstnames', user_name)}\nSexe : {details.get('gender', 'Non renseigné')}\nNé(e) le : {details.get('birth_date', 'Non renseigné')} à Brignon-les-Bains\n\nPère : {details.get('father_name', 'Non renseigné')}\nMère : {details.get('mother_name', 'Non renseigné')}\n\nDocument délivré le {today} par l'officier de l'état civil délégué.\nCertifié conforme au registre.",
            "next": "Pour toute démarche officielle nécessitant un acte avec valeur légale, veuillez faire votre demande via service-public.fr."
        }
    }
    
    doc_info = doc_types.get(doc_type.lower(), doc_types["courrier_officiel"])
    
    doc += f"TITRE DU DOCUMENT : {doc_info['title']}\n"
    doc += f"SERVICE ÉMETTEUR  : {doc_info['service']}\n"
    doc += f"USAGER CONCERNÉ   : {user_name}\n"
    doc += f"OBJET DE LA FICHE : {doc_info['object']}\n"
    doc += "-" * 80 + "\n\n"
    doc += f"{doc_info['body']}\n\n"
    doc += "-" * 80 + "\n"
    doc += f"PROCHAINES ÉTAPES : {doc_info['next']}\n"
    doc += "=" * 80 + "\n"
    doc += " MENTION LÉGALE : Document fictif généré dans le cadre d'une démonstration\n"
    doc += "                  — SANS VALEUR ADMINISTRATIVE OU JURIDIQUE —\n"
    doc += "=" * 80 + "\n"
    
    if tool_context:
        try:
            # Generate PDF bytes
            pdf_bytes = create_pdf_bytes(
                title=doc_info["title"],
                service=doc_info["service"],
                user_name=user_name,
                obj=doc_info["object"],
                body=doc_info["body"],
                next_steps=doc_info["next"],
                date_str=today,
                dossier_id=dossier_id
            )
            
            filename = f"document_fictif_{dossier_id}.pdf"
            part = types.Part(inline_data=types.Blob(mime_type="application/pdf", data=pdf_bytes))
            
            # Get variables
            user_id = tool_context._invocation_context.user_id or "default_user"
            session_id = tool_context._invocation_context.session.id or "default_session"
            app_name = tool_context._invocation_context.app_name or "app"
            
            try:
                await tool_context.save_artifact(filename, part)
            except Exception as e:
                # Log warning but do not fail; still generate link for local evaluation/testing
                import logging
                logging.getLogger("app").warning(f"Could not save artifact: {e}")
            
            # Formulate the download URL
            download_url = f"http://localhost:8000/download/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{filename}"
            doc += f"\n📥 [Télécharger le document PDF officiel de démonstration]({download_url})\n"
        except Exception as e:
            doc += f"\n(Note : La génération du PDF a échoué : {str(e)})\n"
            
    return doc
