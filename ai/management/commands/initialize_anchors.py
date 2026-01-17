"""
Django management command to initialize anchor clauses.

Usage:
    python manage.py initialize_anchors
"""

from django.core.management.base import BaseCommand
from ai.models import ClauseAnchor
from repository.embeddings_service import VoyageEmbeddingsService
import logging

logger = logging.getLogger(__name__)

ANCHOR_CLAUSES = [
    {
        'label': 'Confidentiality',
        'category': 'Legal',
        'description': 'Clause governing confidential information and trade secrets',
        'example_text': """The parties agree to maintain the confidentiality of all non-public information 
        disclosed in connection with this Agreement. Confidential Information includes but is not limited to 
        technical data, business plans, customer lists, and financial information. Each party agrees not to 
        disclose Confidential Information to third parties without prior written consent, except as required by law."""
    },
    {
        'label': 'Limitation of Liability',
        'category': 'Legal',
        'description': 'Clause limiting damages and liability exposure',
        'example_text': """IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, 
        CONSEQUENTIAL OR PUNITIVE DAMAGES ARISING OUT OF OR RELATED TO THIS AGREEMENT. Each party's total 
        liability under this Agreement shall not exceed the amounts paid or payable under this Agreement in 
        the 12 months preceding the claim."""
    },
    {
        'label': 'Indemnification',
        'category': 'Legal',
        'description': 'Clause requiring one party to compensate the other for losses',
        'example_text': """Provider shall indemnify, defend, and hold harmless Client from and against any 
        and all claims, damages, losses, and expenses (including reasonable attorneys fees) arising from or 
        relating to Provider's breach of this Agreement, violation of applicable law, or infringement of 
        intellectual property rights of third parties."""
    },
    {
        'label': 'Termination',
        'category': 'Operational',
        'description': 'Clause specifying conditions and procedures for contract termination',
        'example_text': """This Agreement may be terminated (a) by either party upon 30 days written notice 
        for material breach that is not cured within 15 days of notice, or (b) by either party immediately 
        upon written notice if the other party becomes insolvent or files for bankruptcy. Upon termination, 
        all obligations cease except those that by their nature are intended to survive termination."""
    },
    {
        'label': 'Payment Terms',
        'category': 'Financial',
        'description': 'Clause specifying payment amounts, timing, and conditions',
        'example_text': """Client shall pay Provider the fees as follows: (a) 50% upon execution of this 
        Agreement, (b) 50% upon delivery and acceptance of deliverables. Payments shall be made within 
        30 days of invoice. Late payments shall accrue interest at 1.5% per month. All fees are exclusive 
        of applicable sales taxes."""
    },
    {
        'label': 'Intellectual Property',
        'category': 'Legal',
        'description': 'Clause addressing ownership and rights to intellectual property',
        'example_text': """Provider retains all right, title, and interest in any pre-existing intellectual 
        property and tools developed independently. Work Product created specifically for Client under this 
        Agreement shall be owned by Client. Provider grants Client a royalty-free license to use any 
        third-party components in the Work Product for Client's internal use."""
    },
    {
        'label': 'Governing Law',
        'category': 'Legal',
        'description': 'Clause specifying which jurisdiction laws govern the agreement',
        'example_text': """This Agreement shall be governed by and construed in accordance with the laws of 
        the State of New York, without regard to its conflict of law principles. The parties irrevocably 
        agree to submit to the exclusive jurisdiction of the courts located in New York."""
    },
    {
        'label': 'Dispute Resolution',
        'category': 'Legal',
        'description': 'Clause outlining procedures for resolving disputes',
        'example_text': """Any dispute arising from this Agreement shall first be resolved through good faith 
        negotiation between senior executives. If negotiation fails, disputes shall be submitted to binding 
        arbitration under the rules of the American Arbitration Association. Arbitration shall occur in 
        New York and shall be governed by the Federal Arbitration Act."""
    },
    {
        'label': 'Warranty Disclaimer',
        'category': 'Legal',
        'description': 'Clause disclaiming warranties and representations',
        'example_text': """EXCEPT AS EXPRESSLY PROVIDED HEREIN, PROVIDER MAKES NO OTHER WARRANTIES, EXPRESS 
        OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR 
        NON-INFRINGEMENT. The Services are provided "AS IS" and Provider does not warrant that Services 
        will be uninterrupted or error-free."""
    },
    {
        'label': 'Force Majeure',
        'category': 'Legal',
        'description': 'Clause excusing performance due to unforeseen circumstances',
        'example_text': """Neither party shall be liable for failure to perform obligations due to events 
        beyond reasonable control including acts of God, war, terrorism, pandemic, government action, or 
        natural disasters. The affected party must provide prompt notice and use reasonable efforts to 
        mitigate impact. Obligations are suspended during the force majeure event."""
    },
    {
        'label': 'Representations and Warranties',
        'category': 'Legal',
        'description': 'Clause containing statements and assurances by the parties',
        'example_text': """Each party represents and warrants that: (a) it has full power and authority to 
        enter into this Agreement, (b) the signatory is duly authorized, (c) this Agreement constitutes 
        valid and binding obligation, (d) execution does not violate any other agreement or law, and 
        (e) all information provided is accurate and complete."""
    },
    {
        'label': 'Non-Disclosure Agreement',
        'category': 'Legal',
        'description': 'Clause preventing disclosure of proprietary information',
        'example_text': """Recipient agrees not to disclose Sender's confidential information except (a) to 
        employees with legitimate need to know, (b) when required by law or court order, or (c) with prior 
        written consent. Recipient shall protect information with same care as its own confidential 
        information but no less than reasonable care."""
    },
    {
        'label': 'Services Description',
        'category': 'Operational',
        'description': 'Clause describing the services or deliverables provided',
        'example_text': """Provider shall provide the following services: (a) Technical consulting (40 hours/month), 
        (b) Code review and quality assurance, (c) Documentation and knowledge transfer, (d) 24-hour incident 
        response for critical issues. All services shall be performed in a professional manner according to 
        industry standards."""
    },
    {
        'label': 'Assignment and Delegation',
        'category': 'Legal',
        'description': 'Clause restricting assignment of rights or obligations',
        'example_text': """Neither party may assign its rights or delegate its obligations under this Agreement 
        without prior written consent of the other party, except in connection with a merger, acquisition, or 
        sale of substantially all assets. Any attempted assignment in violation of this clause shall be void. 
        This Agreement shall bind and inure to the benefit of the parties and their permitted successors."""
    },
]


class Command(BaseCommand):
    help = 'Initialize anchor clauses for clause classification with pre-computed embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing anchor clauses before initializing'
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = ClauseAnchor.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Cleared {count} existing anchor clauses'))

        embeddings_service = VoyageEmbeddingsService()
        created_count = 0
        updated_count = 0
        failed_count = 0

        for clause_data in ANCHOR_CLAUSES:
            try:
                # Generate embedding for example text
                example_embedding = embeddings_service.embed_text(clause_data['example_text'])

                if not example_embedding:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to generate embedding for {clause_data["label"]}')
                    )
                    failed_count += 1
                    continue

                # Create or update anchor clause
                anchor, created = ClauseAnchor.objects.update_or_create(
                    label=clause_data['label'],
                    defaults={
                        'description': clause_data['description'],
                        'category': clause_data['category'],
                        'example_text': clause_data['example_text'],
                        'embedding': example_embedding,
                        'is_active': True,
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {clause_data["label"]} ({clause_data["category"]})')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'↻ Updated: {clause_data["label"]} ({clause_data["category"]})')
                    )

            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {clause_data["label"]}: {str(e)}')
                )

        # Summary
        active_count = ClauseAnchor.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Initialization Complete!\n'
                f'  Created: {created_count}\n'
                f'  Updated: {updated_count}\n'
                f'  Failed: {failed_count}\n'
                f'  Total Active Anchors: {active_count}'
            )
        )
