export const OpenAPI = {
    BASE: 'http://192.168.186.138:8000',
    CREDENTIALS: 'include',
    ENCODE_PATH: undefined,
    HEADERS: undefined,
    PASSWORD: undefined,
    RESULT: 'body',
    TOKEN: undefined,
    USERNAME: undefined,
    VERSION: '0.1.0',
    WITH_CREDENTIALS: false,
};
export const mergeOpenApiConfig = (config, overrides) => {
    const merged = { ...config };
    Object.entries(overrides)
        .filter(([key]) => key.startsWith('_'))
        .forEach(([key, value]) => {
        const k = key.slice(1).toLocaleUpperCase();
        if (merged.hasOwnProperty(k)) {
            // @ts-ignore
            merged[k] = value;
        }
    });
    return merged;
};
//# sourceMappingURL=OpenAPI.js.map