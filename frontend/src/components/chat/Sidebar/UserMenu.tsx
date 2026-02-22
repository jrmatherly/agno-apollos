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

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

function MsalUserMenu() {
  useTokenSync()
  const { isAuthenticated, account, login, logout } = useAuth()

  if (!isAuthenticated) {
    return (
      <button
        onClick={login}
        className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs font-medium text-muted transition-colors hover:bg-accent hover:text-primary"
      >
        <Avatar className="h-7 w-7">
          <AvatarFallback className="bg-accent text-[10px] text-muted">
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
        <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs font-medium text-muted transition-colors hover:bg-accent hover:text-primary focus:outline-none">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="bg-brand/20 text-[10px] font-semibold text-brand">
              {initials}
            </AvatarFallback>
          </Avatar>
          <span className="flex-1 truncate text-left">{displayName}</span>
          <Icon type="chevron-up" size="xs" className="shrink-0 opacity-50" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        side="top"
        align="start"
        className="w-56 border-border bg-primaryAccent font-geist"
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
        <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs font-medium text-muted transition-colors hover:bg-accent hover:text-primary focus:outline-none">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="bg-accent text-[10px] text-muted">
              <Icon type="user" size="xs" />
            </AvatarFallback>
          </Avatar>
          <span className="flex-1 truncate text-left">User</span>
          <Icon type="chevron-up" size="xs" className="shrink-0 opacity-50" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        side="top"
        align="start"
        className="w-56 border-border bg-primaryAccent font-geist"
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
