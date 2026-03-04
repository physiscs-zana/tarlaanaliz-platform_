// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
import { useMemo } from 'react';

import type { AuthRole } from './useAuth';

export function useRoleGuard(currentRole: AuthRole | null | undefined, allowedRoles: AuthRole[]) {
  return useMemo(() => {
    const allowed = !!currentRole && allowedRoles.includes(currentRole);
    return {
      allowed,
      forbidden: !allowed,
      requiredRoles: allowedRoles
    };
  }, [allowedRoles, currentRole]);
}
