/**
 * NavbarItem Wrapper
 * Feature: 003-better-auth
 *
 * This wrapper component intercepts navbar items and renders the AuthButton
 * when the item has className 'header-auth-btn'.
 *
 * This is the Docusaurus way to "swizzle" components without ejecting the entire theme.
 */

import React from 'react';
import OriginalNavbarItem from '@theme-original/NavbarItem';
import AuthButton from './AuthButton';
import type { Props } from '@theme/NavbarItem';

export default function NavbarItem(props: Props): JSX.Element {
  // Check if this is our custom auth button item
  if (props.className === 'header-auth-btn') {
    return <AuthButton />;
  }

  // Otherwise, render the original navbar item
  return <OriginalNavbarItem {...props} />;
}
