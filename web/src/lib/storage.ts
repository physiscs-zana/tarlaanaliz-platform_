// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

export interface StorageAdapter {
  get: (key: string) => string | null;
  set: (key: string, value: string) => void;
  remove: (key: string) => void;
}

export function createLocalStorageAdapter(): StorageAdapter {
  return {
    get: (key) => (typeof window === 'undefined' ? null : window.localStorage.getItem(key)),
    set: (key, value) => {
      if (typeof window !== 'undefined') window.localStorage.setItem(key, value);
    },
    remove: (key) => {
      if (typeof window !== 'undefined') window.localStorage.removeItem(key);
    }
  };
}

// Auth token yönetimi için authStorage.ts kanonik kaynaktır.
// Token key: authStorage.ts tarafından yönetilir, burada tekrar tanımlanmaz.
