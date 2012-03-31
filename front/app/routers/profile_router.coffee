class exports.ProfileRouter extends Backbone.Router
  routes:
    '!/profiles/': "index"
    '!/profiles/:id': "show"
    '!/profiles/:id/edit': "edit"

  initialize: (options) ->
    @mainRouter = options.mainRouter

  index: ->
    console.log 'index'

  show: (id) ->
    profileView = @_render(ProfileView, {id: id})
    console.log 'index'

  edit: ->
    console.log 'index'
