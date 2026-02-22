'use client'

import { type FC, useState } from 'react'
import Image from 'next/image'
import * as DialogPrimitive from '@radix-ui/react-dialog'
import Icon from '@/components/ui/icon'
import { MCPSettingsContent } from '@/app/settings/mcp/MCPSettingsContent'
import { M365SettingsContent } from '@/app/settings/m365/M365SettingsContent'

type SettingsSection = 'general' | 'm365' | 'mcp'

interface NavItem {
  id: SettingsSection
  label: string
  icon: 'settings' | 'azure' | 'hammer'
}

const NAV_ITEMS: NavItem[] = [
  { id: 'general', label: 'General', icon: 'settings' },
  { id: 'm365', label: 'Microsoft 365', icon: 'azure' },
  { id: 'mcp', label: 'MCP Gateway', icon: 'hammer' }
]

const SECTION_META: Record<
  SettingsSection,
  { title: string; description: string }
> = {
  general: {
    title: 'General',
    description: 'Overview and system preferences'
  },
  m365: {
    title: 'Microsoft 365',
    description:
      'Connect your account to access OneDrive, SharePoint, Outlook, Calendar, and Teams'
  },
  mcp: {
    title: 'MCP Gateway',
    description: 'Manage Model Context Protocol connections and resources'
  }
}

function GeneralContent() {
  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-white/10 bg-white/[0.03] p-6">
        <h3 className="mb-1 text-sm font-semibold text-slate-200">
          Apollos AI
        </h3>
        <p className="text-xs text-slate-400">
          Multi-agent system powered by the Agno framework. Configure
          integrations and manage connected services below.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
            Integrations
          </p>
          <p className="mt-1 text-lg font-bold text-slate-200">2</p>
          <p className="text-xs text-slate-400">Available services</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
            Status
          </p>
          <p className="mt-1 flex items-center gap-2 text-lg font-bold text-slate-200">
            <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
            Online
          </p>
          <p className="text-xs text-slate-400">All systems operational</p>
        </div>
      </div>
    </div>
  )
}

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

const SettingsModal: FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState<SettingsSection>('general')

  const meta = SECTION_META[activeSection]

  return (
    <DialogPrimitive.Root open={isOpen} onOpenChange={onClose}>
      <DialogPrimitive.Portal>
        {/* Overlay */}
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />

        {/* Modal content */}
        <DialogPrimitive.Content
          className="fixed left-1/2 top-1/2 z-50 flex h-[85vh] w-full max-w-5xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-2xl border border-white/[0.08] shadow-[0_0_0_1px_rgba(0,212,255,0.05),0_25px_50px_-12px_rgba(0,0,0,0.7)] duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]"
          style={{
            background:
              'linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(10, 16, 29, 0.98))',
            backdropFilter: 'blur(40px)'
          }}
        >
          {/* Header */}
          <header className="flex shrink-0 items-center justify-between border-b border-white/10 px-8 py-5">
            <div className="flex items-center gap-3">
              <div className="relative flex h-10 w-10 items-center justify-center">
                <div className="absolute inset-0 rounded-full bg-blue-500/20 blur-md" />
                <Image
                  src="/apollos_round_no_bg.svg"
                  alt="Apollos AI"
                  width={32}
                  height={32}
                  className="relative z-10"
                />
              </div>
              <div>
                <DialogPrimitive.Title className="text-lg font-bold leading-tight tracking-tight text-slate-100">
                  Apollos AI
                </DialogPrimitive.Title>
                <DialogPrimitive.Description className="text-xs font-medium text-slate-400">
                  Settings
                </DialogPrimitive.Description>
              </div>
            </div>
            <DialogPrimitive.Close className="flex h-10 w-10 items-center justify-center rounded-full bg-white/5 text-slate-300 transition-colors hover:bg-white/10">
              <Icon type="x" size="xs" />
              <span className="sr-only">Close</span>
            </DialogPrimitive.Close>
          </header>

          {/* Body: sidebar + content */}
          <div className="flex min-h-0 flex-1">
            {/* Sidebar */}
            <aside className="flex w-56 shrink-0 flex-col border-r border-white/10 py-6">
              <nav className="flex-1 space-y-1 px-4">
                {NAV_ITEMS.map((item) => {
                  const isActive = activeSection === item.id
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveSection(item.id)}
                      className={`flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left text-sm font-semibold transition-all ${
                        isActive
                          ? 'border-sky-400/20 bg-sky-400/[0.12] text-sky-400 shadow-[0_0_15px_rgba(0,212,255,0.05)]'
                          : 'border-transparent text-slate-400 hover:border-white/10 hover:bg-white/5 hover:text-slate-100'
                      }`}
                    >
                      <Icon type={item.icon} size="xs" />
                      <span>{item.label}</span>
                    </button>
                  )
                })}
              </nav>

              {/* System status mini-card */}
              <div className="mt-auto px-4 pt-4">
                <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.6)]" />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                      System Status
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">Gateway operational</p>
                  <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-white/10">
                    <div className="h-full w-full bg-emerald-500 opacity-50" />
                  </div>
                </div>
              </div>
            </aside>

            {/* Content area */}
            <main className="flex min-h-0 flex-1 flex-col overflow-hidden bg-black/10">
              {/* Content header */}
              <div className="shrink-0 px-8 pt-6">
                <h2 className="text-xl font-bold tracking-tight text-slate-100">
                  {meta.title}
                </h2>
                <p className="mt-1 text-sm text-slate-400">
                  {meta.description}
                </p>
              </div>

              {/* Scrollable content */}
              <div className="scrollbar-none flex-1 overflow-y-auto p-8">
                {activeSection === 'general' && <GeneralContent />}
                {activeSection === 'm365' && <M365SettingsContent />}
                {activeSection === 'mcp' && <MCPSettingsContent />}
              </div>
            </main>
          </div>

          {/* Footer */}
          <footer className="flex shrink-0 items-center justify-between border-t border-white/10 bg-black/20 px-8 py-4">
            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1.5">
                <Icon type="check" size="xs" />
                Encryption Active
              </span>
              <span className="flex items-center gap-1.5">
                <Icon type="database" size="xs" />
                PostgreSQL
              </span>
            </div>
            <button
              onClick={onClose}
              className="rounded-full px-6 py-2 text-sm font-bold text-slate-400 transition-all hover:text-slate-100"
            >
              Close
            </button>
          </footer>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}

export default SettingsModal
