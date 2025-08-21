from django.core.management.base import BaseCommand
from chatbot.models import Node, Option

class Command(BaseCommand):
    help = 'Sets up CPI Technologies nodes for the chatbot'

    def handle(self, *args, **options):
        # Clear existing data
        Node.objects.all().delete()
        
        # Create nodes
        greeting = Node.objects.create(
            name="greeting",
            message="Welcome to CPI Technologies! We're a leading provider of innovative technology solutions. How can I assist you today?",
            is_start=True
        )
        
        services = Node.objects.create(
            name="services",
            message="CPI Technologies offers a comprehensive range of services:\n\n"
                   "• IT Consulting & Strategy\n"
                   "• Custom Software Development\n"
                   "• Cloud Solutions & Migration\n"
                   "• Cybersecurity Services\n"
                   "• Data Analytics & Business Intelligence\n"
                   "• Managed IT Services\n"
                   "• Digital Transformation\n\n"
                   "Which service are you interested in learning more about?"
        )
        
        it_consulting = Node.objects.create(
            name="it_consulting",
            message="Our IT Consulting services help businesses align technology with their strategic goals. "
                   "We provide:\n\n"
                   "• Technology Assessment & Planning\n"
                   "• IT Infrastructure Design\n"
                   "• System Integration Consulting\n"
                   "• IT Governance & Compliance\n"
                   "• Digital Strategy Development\n\n"
                   "Would you like to schedule a consultation?"
        )
        
        software_dev = Node.objects.create(
            name="software_dev",
            message="Our Custom Software Development team creates tailored solutions for your business needs:\n\n"
                   "• Web Application Development\n"
                   "• Mobile App Development (iOS & Android)\n"
                   "• Enterprise Software Solutions\n"
                   "• API Development & Integration\n"
                   "• Legacy System Modernization\n\n"
                   "What type of application are you looking to develop?"
        )
        
        cloud_services = Node.objects.create(
            name="cloud_services",
            message="Our Cloud Solutions help businesses leverage the power of cloud computing:\n\n"
                   "• Cloud Migration Strategy & Execution\n"
                   "• AWS, Azure & Google Cloud Platform Services\n"
                   "• Cloud Infrastructure Management\n"
                   "• DevOps & Continuous Integration\n"
                   "• Cloud Security & Compliance\n\n"
                   "Are you looking to migrate to the cloud or optimize your existing cloud infrastructure?"
        )
        
        cybersecurity = Node.objects.create(
            name="cybersecurity",
            message="Our Cybersecurity Services protect your business from evolving threats:\n\n"
                   "• Security Risk Assessment\n"
                   "• Network Security & Firewall Management\n"
                   "• Endpoint Protection\n"
                   "• Security Awareness Training\n"
                   "• Incident Response & Recovery\n"
                   "• Compliance Management (GDPR, HIPAA, PCI DSS)\n\n"
                   "What security concerns does your business face?"
        )
        
        about = Node.objects.create(
            name="about",
            message="CPI Technologies is a trusted technology partner helping businesses innovate and grow. "
                   "Founded with a vision to deliver exceptional technology solutions, we combine deep expertise "
                   "with cutting-edge technologies to solve complex business challenges.\n\n"
                   "Our team of experienced professionals is dedicated to understanding your unique needs and "
                   "delivering solutions that drive real business value."
        )
        
        contact = Node.objects.create(
            name="contact",
            message="You can reach CPI Technologies through:\n\n"
                   "• Phone: (123) 456-7890\n"
                   "• Email: info@cpitechinc.com\n"
                   "• Website: www.cpitechinc.com\n"
                   "• Address: 123 Tech Boulevard, Innovation City, IC 12345\n\n"
                   "Would you like to speak with a specific department?"
        )
        
        pricing = Node.objects.create(
            name="pricing",
            message="Our pricing depends on the specific services and scope of your project. "
                   "We offer:\n\n"
                   "• Project-based pricing for defined scope projects\n"
                   "• Time and materials for ongoing work\n"
                   "• Retainer agreements for ongoing support\n"
                   "• Managed service plans\n\n"
                   "Would you like us to prepare a custom quote for your needs?"
        )
        
        case_studies = Node.objects.create(
            name="case_studies",
            message="We've helped numerous businesses achieve their technology goals. Here are some examples:\n\n"
                   "• Financial Services Firm: Streamlined operations with custom workflow system\n"
                   "• Healthcare Provider: Implemented secure patient data management system\n"
                   "• Retail Chain: Developed omnichannel e-commerce platform\n"
                   "• Manufacturing Company: IoT implementation for predictive maintenance\n\n"
                   "Which industry are you interested in hearing more about?"
        )
        
        # Create options (conversation paths)
        Option.objects.create(keyword="services", from_node=greeting, to_node=services)
        Option.objects.create(keyword="what services", from_node=greeting, to_node=services)
        Option.objects.create(keyword="offerings", from_node=greeting, to_node=services)
        Option.objects.create(keyword="solutions", from_node=greeting, to_node=services)
        
        Option.objects.create(keyword="about", from_node=greeting, to_node=about)
        Option.objects.create(keyword="who are you", from_node=greeting, to_node=about)
        Option.objects.create(keyword="company", from_node=greeting, to_node=about)
        
        Option.objects.create(keyword="contact", from_node=greeting, to_node=contact)
        Option.objects.create(keyword="get in touch", from_node=greeting, to_node=contact)
        Option.objects.create(keyword="phone", from_node=greeting, to_node=contact)
        Option.objects.create(keyword="email", from_node=greeting, to_node=contact)
        
        Option.objects.create(keyword="pricing", from_node=greeting, to_node=pricing)
        Option.objects.create(keyword="cost", from_node=greeting, to_node=pricing)
        Option.objects.create(keyword="price", from_node=greeting, to_node=pricing)
        
        Option.objects.create(keyword="examples", from_node=greeting, to_node=case_studies)
        Option.objects.create(keyword="case studies", from_node=greeting, to_node=case_studies)
        Option.objects.create(keyword="portfolio", from_node=greeting, to_node=case_studies)
        
        # Services sub-options
        Option.objects.create(keyword="it consulting", from_node=services, to_node=it_consulting)
        Option.objects.create(keyword="consulting", from_node=services, to_node=it_consulting)
        
        Option.objects.create(keyword="software", from_node=services, to_node=software_dev)
        Option.objects.create(keyword="development", from_node=services, to_node=software_dev)
        Option.objects.create(keyword="app", from_node=services, to_node=software_dev)
        
        Option.objects.create(keyword="cloud", from_node=services, to_node=cloud_services)
        Option.objects.create(keyword="aws", from_node=services, to_node=cloud_services)
        Option.objects.create(keyword="azure", from_node=services, to_node=cloud_services)
        
        Option.objects.create(keyword="security", from_node=services, to_node=cybersecurity)
        Option.objects.create(keyword="cybersecurity", from_node=services, to_node=cybersecurity)
        Option.objects.create(keyword="hack", from_node=services, to_node=cybersecurity)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up CPI Technologies nodes with sample data')
        )