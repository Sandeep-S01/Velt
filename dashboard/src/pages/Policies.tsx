import React from 'react';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

interface PolicySection {
  heading: string;
  paragraphs?: string[];
  items?: string[];
}

interface PolicyPageProps {
  eyebrow: string;
  title: string;
  introduction: string;
  sections: PolicySection[];
}

const PolicyPage: React.FC<PolicyPageProps> = ({ eyebrow, title, introduction, sections }) => (
  <div className="min-h-screen bg-neutral-background text-neutral-charcoal">
    <header className="border-b border-neutral-lightgray bg-white">
      <div className="max-w-4xl mx-auto px-6 py-5 flex items-center justify-between gap-4">
        <Link to="/" className="text-xl font-black tracking-tight text-brand">Velt</Link>
        <Link to="/" className="inline-flex items-center gap-2 text-sm font-bold text-neutral-darkgray hover:text-brand">
          <ArrowLeft className="w-4 h-4" /> Back to Velt
        </Link>
      </div>
    </header>

    <main className="max-w-4xl mx-auto px-6 py-14 md:py-20">
      <article className="bg-white border border-neutral-lightgray rounded-3xl p-7 md:p-12 shadow-sm">
        <div className="pb-8 border-b border-neutral-lightgray">
          <p className="text-xs font-extrabold uppercase tracking-widest text-brand">{eyebrow}</p>
          <h1 className="mt-3 text-4xl md:text-5xl font-black tracking-tight">{title}</h1>
          <p className="mt-5 text-base text-neutral-mediumgray font-medium leading-relaxed">{introduction}</p>
          <p className="mt-4 text-xs font-semibold text-neutral-mediumgray">Private beta version · Last updated September 19, 2026</p>
        </div>

        <div className="pt-8 space-y-9">
          {sections.map((section) => (
            <section key={section.heading} className="space-y-3">
              <h2 className="text-xl font-extrabold">{section.heading}</h2>
              {section.paragraphs?.map((paragraph) => (
                <p key={paragraph} className="text-sm md:text-base text-neutral-darkgray leading-7">{paragraph}</p>
              ))}
              {section.items && (
                <ul className="list-disc pl-5 space-y-2 text-sm md:text-base text-neutral-darkgray leading-7">
                  {section.items.map((item) => <li key={item}>{item}</li>)}
                </ul>
              )}
            </section>
          ))}
        </div>

        <div className="mt-10 pt-7 border-t border-neutral-lightgray text-sm text-neutral-darkgray">
          Questions or requests can be sent to{' '}
          <a className="font-bold text-brand hover:underline inline-flex items-center gap-1" href="mailto:support@velt.ai">
            support@velt.ai <ExternalLink className="w-3.5 h-3.5" />
          </a>.
        </div>
      </article>
    </main>
  </div>
);

export const PrivacyPolicy: React.FC = () => (
  <PolicyPage
    eyebrow="Legal"
    title="Privacy Policy"
    introduction="This policy explains the data Velt processes to provide semantic product search and merchant analytics during the private beta."
    sections={[
      { heading: 'Data we process', paragraphs: ['Velt processes merchant account information, store metadata, catalog data, search queries, click events, API usage metadata, and integration credentials required to operate the service.'] },
      { heading: 'How we use data', paragraphs: ['We use this data to ingest catalogs, build search indexes, serve storefront results, generate merchant analytics, secure the service, prevent abuse, and provide support.'] },
      { heading: 'Data sharing', paragraphs: ['Velt does not sell merchant catalog or shopper query data. Data is shared only with infrastructure providers needed to operate Velt, authorities when legally required, and integrations authorized by the merchant.'] },
      { heading: 'Retention', paragraphs: ['Account, catalog, analytics, and integration data is retained while needed to provide the beta service or until deletion is requested, subject to the published Data Retention Policy and backup expiration.'] },
      { heading: 'Security', paragraphs: ['Velt uses access controls, hashed API keys, encrypted integration tokens, production configuration validation, network restrictions, backups, monitoring, and incident response procedures.'] },
      { heading: 'Merchant controls', paragraphs: ['Merchants may request access, correction, export, or deletion of their account and catalog data by contacting support. Deletion includes derived search indexes; backup copies expire through the backup lifecycle.'] },
    ]}
  />
);

export const TermsOfService: React.FC = () => (
  <PolicyPage
    eyebrow="Legal"
    title="Terms of Service"
    introduction="These beta terms govern access to Velt's catalog ingestion, semantic search, storefront widget, and merchant analytics services."
    sections={[
      { heading: 'Beta service', paragraphs: ['Velt is a private beta service. Features may change as reliability, relevance, and operating limits are measured. The beta has no guaranteed service-level agreement.'] },
      { heading: 'Merchant responsibilities', paragraphs: ['Merchants must have the right to upload and process their catalog data, configure only storefronts they control, protect private credentials, and comply with laws that apply to their stores and shoppers.'] },
      { heading: 'Acceptable use', items: ['Do not upload unlawful or unauthorized content.', 'Do not attack the service, bypass rate limits, or probe another merchant’s data.', 'Do not share private API keys or beta invitations publicly.', 'Do not use Velt to process data you are not authorized to process.'] },
      { heading: 'Data and integrations', paragraphs: ['Merchants authorize Velt to process catalog, query, click, and integration data as needed to provide the service. Shopify and other third-party integrations remain subject to their own terms.'] },
      { heading: 'Suspension and termination', paragraphs: ['A merchant may stop using Velt and request deletion. Velt may suspend beta access to protect the service, investigate abuse or security issues, comply with law, or end the beta.'] },
      { heading: 'Changes', paragraphs: ['These terms may be updated as the beta changes. The current version and its update date will remain available on this page. Material changes will be communicated to active beta merchants through available contact information.'] },
    ]}
  />
);

export const DataRetentionPolicy: React.FC = () => (
  <PolicyPage
    eyebrow="Data governance"
    title="Data Retention Policy"
    introduction="Velt keeps data only for the periods needed to operate the private beta, provide merchant analytics, recover the service, and meet legal obligations."
    sections={[
      { heading: 'Default retention periods', items: ['Merchant account data: while the account is active.', 'Catalog data and derived search indexes: while the store is active.', 'Search query logs and click events: up to 180 days.', 'Raw uploaded files: up to 30 days after ingestion or quarantine.', 'Integration credentials: while the integration remains active.', 'Infrastructure backups: up to 30 days, subject to the configured provider schedule.'] },
      { heading: 'Deletion', paragraphs: ['A deletion request removes account-owned stores, products, credentials, query logs, click events, and derived search indexes from active systems. Backup copies expire through the normal backup lifecycle unless earlier deletion is legally required and operationally supported.'] },
      { heading: 'Data minimization', paragraphs: ['Velt does not require shopper names or contact details for search analytics. Merchants should avoid placing personal or sensitive information in product data or search configuration.'] },
      { heading: 'Review', paragraphs: ['Retention settings are reviewed before the beta expands and at least quarterly while the service remains active.'] },
    ]}
  />
);

export const SupportAndIncidents: React.FC = () => (
  <PolicyPage
    eyebrow="Support"
    title="Support and Incident Reporting"
    introduction="Beta merchants can use the support channel for product help, privacy requests, data deletion, and suspected security incidents."
    sections={[
      { heading: 'Contacting support', paragraphs: ['Email support@velt.ai and include the affected store, a description of the problem, when it began, and any safe reproduction steps. Never include passwords, API keys, Shopify access tokens, or shopper personal data.'] },
      { heading: 'Security incidents', paragraphs: ['Mark suspected credential exposure, cross-tenant access, storefront script injection, or unexpected data disclosure as a security incident. Revoke affected keys from the dashboard when possible.'] },
      { heading: 'Response process', items: ['Triage the report and identify affected services and merchants.', 'Contain access or disable affected credentials when needed.', 'Preserve relevant security and operational evidence.', 'Recover service and verify that the issue no longer reproduces.', 'Notify affected merchants and authorities when required.', 'Record follow-up actions that reduce recurrence.'] },
      { heading: 'Beta support level', paragraphs: ['Support and incident response are provided on a best-effort basis during the private beta. No response-time or availability SLA is currently offered.'] },
    ]}
  />
);
