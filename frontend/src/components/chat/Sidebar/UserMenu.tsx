'use client'

import Link from 'next/link'
import Icon from '@/components/ui/icon'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { isMsalConfigured, useAuth, useTokenSync } from '@/auth'
import { getInitials } from '@/lib/utils'

function MsalUserMenu() {
  useTokenSync()
  const { isAuthenticated, account, login, logout } = useAuth()

  if (!isAuthenticated) {
    return (
      <button
        onClick={login}
        className="group relative flex w-full items-center gap-3 overflow-hidden rounded-full border border-white/5 bg-primaryAccent p-3 text-xs font-medium text-muted transition-all hover:border-white/10"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-sky-500/10 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
        <Avatar className="h-8 w-8">
          <AvatarFallback className="bg-gradient-to-br from-slate-700 to-slate-800 text-[10px] text-slate-200 ring-1 ring-black/50">
            <Icon type="user" size="xs" />
          </AvatarFallback>
        </Avatar>
        <span>Sign In</span>
      </button>
    )
  }

  const displayName =
    account?.name || account?.username || account?.localAccountId || 'User'
  const email = account?.username || ''
  const initials = getInitials(displayName)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="group relative flex w-full items-center gap-3 overflow-hidden rounded-full border border-white/5 bg-primaryAccent p-3 text-xs font-medium text-muted transition-all hover:border-white/10 focus:outline-none">
          <div className="absolute inset-0 bg-gradient-to-r from-sky-500/10 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
          <div className="relative">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="border border-white/10 bg-gradient-to-br from-slate-700 to-slate-800 text-[10px] font-semibold text-slate-200 ring-1 ring-black/50">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-background bg-emerald-500" />
          </div>
          <span className="flex-1 truncate text-left text-sm font-medium text-slate-200">
            {displayName}
          </span>
          <Icon type="chevron-up" size="xs" className="shrink-0 opacity-50" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        side="top"
        align="start"
        className="w-56 border border-white/10 bg-primaryAccent font-sans backdrop-blur-xl"
      >
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col gap-1">
            <p className="text-sm font-medium">{displayName}</p>
            {email && <p className="text-xs text-muted">{email}</p>}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/settings" className="cursor-pointer">
            <Icon type="settings" size="xs" />
            <span>Settings</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={logout}
          className="cursor-pointer text-destructive focus:text-destructive"
        >
          <Icon type="log-out" size="xs" />
          <span>Sign Out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

function TokenUserMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="group relative flex w-full items-center gap-3 overflow-hidden rounded-full border border-white/5 bg-primaryAccent p-3 text-xs font-medium text-muted transition-all hover:border-white/10 focus:outline-none">
          <div className="absolute inset-0 bg-gradient-to-r from-sky-500/10 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
          <div className="relative">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="border border-white/10 bg-gradient-to-br from-slate-700 to-slate-800 text-[10px] text-slate-200 ring-1 ring-black/50">
                <Icon type="user" size="xs" />
              </AvatarFallback>
            </Avatar>
            <div className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-background bg-emerald-500" />
          </div>
          <span className="flex-1 truncate text-left text-sm font-medium text-slate-200">
            User
          </span>
          <Icon type="chevron-up" size="xs" className="shrink-0 opacity-50" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        side="top"
        align="start"
        className="w-56 border border-white/10 bg-primaryAccent font-sans backdrop-blur-xl"
      >
        <DropdownMenuItem asChild>
          <Link href="/settings" className="cursor-pointer">
            <Icon type="settings" size="xs" />
            <span>Settings</span>
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function UserMenu() {
  if (isMsalConfigured) {
    return <MsalUserMenu />
  }
  return <TokenUserMenu />
}
