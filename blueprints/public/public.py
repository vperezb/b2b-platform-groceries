import flask

from modules import file_manager, store_manager, item_manager, event_manager, user_manager, geo_manager, utils

public_bp = flask.Blueprint(
    'public', 
    __name__, 
    template_folder='templates', 
    static_folder='static',
    url_prefix='',
    static_url_path='/public/static/public'
)

@public_bp.route('/')
def index():
    id_token = flask.request.cookies.get("token")
    user_data = None

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
    
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')
        return flask.render_template('_index.html', user_data=user_data)
    else:
        return flask.render_template('_index.html', user_data=None)

    

@public_bp.route('/map')
def map():
    id_token = flask.request.cookies.get("token")
    user_data = None
    stores = store_manager._load_stores_from_google_datastore()
    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
        except ValueError as exc:
            flask.flash(str(exc), 'warning')

    return flask.render_template('_map.html', user_data=user_data, stores=stores)


@public_bp.route('/catalog')
def catalog():
    id_token = flask.request.cookies.get("token")
    user_data = None
    stores = store_manager._load_stores_from_google_datastore()
    
    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
        except ValueError as exc:
            flask.flash(str(exc), 'warning')

    catalog = utils.read_csv_to_dict_list('data/product_types.csv')
    return flask.render_template('catalog.html', user_data=user_data, catalog=catalog)


@public_bp.route('/products/<product_type_id>')
def product(product_type_id=None):

    id_token = flask.request.cookies.get("token")
    user_data = None
    
    products = item_manager._load_active_items_by_product_type_id_from_google_datastore(product_type_id)
    
    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
        except ValueError as exc:
            flask.flash(str(exc), 'warning')

    
    return flask.render_template('products.html', user_data=user_data, products=products)


@public_bp.route('/store/<store_code_name>')
def store(store_code_name=None):
    id_token = flask.request.cookies.get("token")
    user_data = None
    store_info = store_manager._load_store_by_code_name_from_google_datastore(store_code_name)

    if store_info != {}:
        store_info['phone'] = store_info['phone_country_prefix'] + \
            store_info['phone']
        
        store_items = item_manager._load_active_items_from_google_datastore(
                store_info['id'])
        
        if id_token:
            try:
                user_data = user_manager._get_authorisation(id_token)
                return flask.render_template('order_to_producer.html',
                                        store_info=store_info,
                                        store_items=store_items,
                                        user_data=user_data
                                            )
            except ValueError as exc:
                return flask.render_template('producer.html',
                                        store_info=store_info,
                                        store_items=store_items,
                                            )
        else:
            return flask.render_template('producer.html',
                                        store_info=store_info,
                                        store_items=store_items,
                                            )
        
    else:
        flask.flash(
            f'La tienda {store_code_name} no existe, ha sido borrada o el propietario la ha renombrado.', 'info')
        return flask.render_template('index.html')


    



@public_bp.route('/review_order')
def review_order    ():
    id_token = flask.request.cookies.get("token")
    
    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)

            flask.flash('Bienvenid@ de nuevo!', 'success')
            
            return flask.redirect(flask.url_for('admin.home'))
        except ValueError as exc:
            return flask.render_template('login.html')

    else:
        return flask.render_template('login.html')


@public_bp.route('/login')
def login():
    id_token = flask.request.cookies.get("token")
    
    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)

            flask.flash('Bienvenid@ de nuevo!', 'success')
            
            return flask.redirect(flask.url_for('admin.home'))
        except ValueError as exc:
            return flask.render_template('login.html')

    else:
        return flask.render_template('login.html')


@public_bp.route('/api/product_types')
def api_product_types():
    catalog = utils.read_csv_to_dict_list('data/product_types.csv')
    return flask.jsonify(catalog)