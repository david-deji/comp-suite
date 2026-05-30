"""Legal article text blocks and recourse paragraphs for postings."""


def rights_notice_initial() -> str:
    """Art. 76 consultation rights (60 days) for initial exercise."""
    return """
<div class="consultation-notice">
  <h3>Renseignements sur les droits prévus par la Loi</h3>
  <p>Conformément à l'article 76 de la Loi sur l'équité salariale, les personnes
  salariées de l'entreprise disposent d'un délai de <strong>60 jours</strong>
  suivant la date du présent affichage pour formuler leurs observations à l'employeur.</p>
  <p>Les observations doivent être transmises par écrit à l'employeur.</p>
</div>
"""


def rights_notice_maintenance() -> str:
    """Art. 76.3 consultation rights for maintenance exercise."""
    return """
<div class="consultation-notice">
  <h3>Renseignements sur les droits prévus par la Loi</h3>
  <p>Conformément à l'article 76.3 de la Loi sur l'équité salariale, les personnes
  salariées de l'entreprise disposent d'un délai de <strong>60 jours</strong>
  suivant la date du présent affichage pour formuler leurs observations à l'employeur.</p>
  <p>Les observations doivent être transmises par écrit à l'employeur.</p>
</div>
"""


def recourse_art100() -> str:
    """Recourse for employer-alone maintenance (art. 100)."""
    return """
<div class="recourse-notice">
  <h3>Renseignements sur les recours et délais</h3>
  <p>Conformément à l'article 100 de la Loi sur l'équité salariale, toute personne
  salariée ou association accréditée qui est en désaccord avec l'évaluation du maintien
  de l'équité salariale peut déposer une plainte à la Commission des normes, de l'équité,
  de la santé et de la sécurité du travail (CNESST) dans un délai de <strong>60 jours</strong>
  suivant l'affichage.</p>
</div>
"""


def recourse_art101() -> str:
    """Bad faith/discrimination recourse (art. 101)."""
    return """
<div class="recourse-notice">
  <h3>Recours en cas de mauvaise foi ou de discrimination</h3>
  <p>Conformément à l'article 101 de la Loi sur l'équité salariale, toute personne
  salariée qui croit que l'exercice d'équité salariale ou l'évaluation du maintien
  a été réalisé de mauvaise foi ou de façon discriminatoire peut déposer une plainte
  à la CNESST dans un délai de <strong>60 jours</strong> suivant l'affichage.</p>
</div>
"""


def nouvel_affichage_notice() -> str:
    """Mention that a nouvel affichage will follow."""
    return """
<div class="nouvel-notice">
  <p>À la suite de la période de consultation de 60 jours, un <strong>nouvel affichage</strong>
  sera effectué conformément à la Loi, indiquant les modifications apportées ou
  confirmant les résultats du présent affichage.</p>
</div>
"""


def formulaire_notice() -> str:
    """Mention of CNESST prescribed form."""
    return """
<div class="formulaire-notice">
  <p>Le formulaire prescrit par la CNESST est disponible sur le site de la Commission
  des normes, de l'équité, de la santé et de la sécurité du travail
  (<a href="https://www.cnesst.gouv.qc.ca">www.cnesst.gouv.qc.ca</a>).
  Ce formulaire doit être utilisé pour le dépôt de toute plainte.</p>
</div>
"""
