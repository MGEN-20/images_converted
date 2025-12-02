# AI Kategoryzator Projektów

Proste narzędzie do automatycznego opisywania, kategoryzowania i segregowania plików graficznych (projekty, wizytówki, banery itp.) przy użyciu AI (OpenAI GPT-4o).

## Wymagania

*   Python 3.10+
*   [uv](https://github.com/astral-sh/uv) (do zarządzania zależnościami)
*   Klucz API OpenAI

## Instalacja

1.  Sklonuj repozytorium:
    ```bash
    git clone git@github.com-mgen:MGEN-20/images_converted.git
    cd images_converted
    ```

2.  Utwórz plik `.env` w głównym katalogu i wklej swój klucz API:
    ```bash
    OPENAI_API_KEY=sk-twoj-klucz-api-tutaj
    ```

## Jak używać

Uruchom skrypt podając ścieżkę do folderu z obrazami:

```bash
uv run python main.py /sciezka/do/twoich/plikow --all
```

### Przykład:

```bash
uv run python main.py projekty-test --all
```

## Co się stanie?

Skrypt wykona 3 kroki:
1.  **Opis**: AI opisze każde zdjęcie.
2.  **Kategorie**: AI wymyśli listę kategorii na podstawie opisów.
3.  **Segregacja**: AI przypisze zdjęcia do kategorii i skopiuje je do odpowiednich folderów.

Wyniki znajdziesz w folderze `results` wewnątrz katalogu wejściowego:
*   `results/descriptions.json` - opisy
*   `results/classified_projects.json` - przypisania
*   `results/Nazwa Kategorii/` - posortowane pliki
