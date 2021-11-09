odoo.define('awesome_theme.search_options', function (require) {
    "use strict";

    const FilterMenu = require('web.FilterMenu')
    const GroupByMenu = require('web.GroupByMenu')
    const FavoriteMenu = require('web.FavoriteMenu')
    const ComparisonMenu = require('web.ComparisonMenu')

    class AwesomeFilterMenu extends FilterMenu {}
    AwesomeFilterMenu.template = "awesome_theme.legacy.FilterMenu"

    class AwesomeGroupMenu extends GroupByMenu {}
    AwesomeGroupMenu.template = "awesome_theme.GroupByMenu"

    class AwesomeFavoriteMenu extends FavoriteMenu {}
    AwesomeFavoriteMenu.template = "awesome_theme.FavoriteMenu"

    class AwesomeComparisonMenu extends ComparisonMenu {}
    AwesomeComparisonMenu.template = "awesome_theme.ComparisonMenu"

    return {
        AwesomeFilterMenu,
        AwesomeGroupMenu,
        AwesomeFavoriteMenu,
        AwesomeComparisonMenu
    }
})