import locale

# Set the entire locale to 'en_US.UTF-8'
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Get the current locale for all categories
current_locale = locale.getlocale(locale.LC_ALL)
print(current_locale)
