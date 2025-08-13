import React, { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';

interface Language {
  code: string;
  name: string;
}

interface LanguageSelectorProps {
  selectedLanguage?: string;
  onLanguageChange?: (language: string) => void;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  selectedLanguage = 'en-US',
  onLanguageChange,
}) => {
  const [currentLanguage, setCurrentLanguage] = useState<string>(selectedLanguage);
  const [availableLanguages, setAvailableLanguages] = useState<Language[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Default languages if API call fails
  const defaultLanguages: Language[] = [
    { code: 'en-US', name: 'English (US)' },
    { code: 'en-GB', name: 'English (UK)' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'zh', name: 'Chinese' },
    { code: 'nl', name: 'Dutch' },
    { code: 'hi', name: 'Hindi' },
    { code: 'ru', name: 'Russian' },
  ];

  useEffect(() => {
    fetchSupportedLanguages();
  }, []);

  const fetchSupportedLanguages = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stt/languages');
      
      if (response.ok) {
        const data = await response.json();
        // Convert the languages object to array format
        const languageArray: Language[] = Object.entries(data.languages).map(([code, name]) => ({
          code,
          name: name as string,
        }));
        setAvailableLanguages(languageArray);
      } else {
        // Use default languages if API call fails
        setAvailableLanguages(defaultLanguages);
      }
    } catch (error) {
      console.error('Error fetching supported languages:', error);
      // Use default languages if API call fails
      setAvailableLanguages(defaultLanguages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLanguageChange = (language: string) => {
    setCurrentLanguage(language);
    if (onLanguageChange) {
      onLanguageChange(language);
    }
  };

  const getCurrentLanguageName = (): string => {
    const language = availableLanguages.find(lang => lang.code === currentLanguage);
    return language ? language.name : currentLanguage;
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-[color:var(--muted-text)]">
        <Globe className="h-4 w-4 animate-spin flex-shrink-0" />
        <span className="text-xs sm:text-sm">Loading...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        <Globe className="h-4 w-4 text-[color:var(--muted-text)] flex-shrink-0" />
        <select
          value={currentLanguage}
          onChange={(e) => handleLanguageChange(e.target.value)}
          className="field px-2 sm:px-3 py-1 text-xs sm:text-sm min-w-[8rem]"
        >
          {availableLanguages.map((language) => (
            <option key={language.code} value={language.code}>
              {language.name}
            </option>
          ))}
        </select>
      </div>
      {/* Language info tooltip - hidden on mobile */}
      <div className="hidden sm:block absolute top-full left-0 mt-1 text-xs text-[color:var(--muted-text)] opacity-0 hover:opacity-100 transition-opacity pointer-events-none">
        Current: {getCurrentLanguageName()}
      </div>
    </div>
  );
};
