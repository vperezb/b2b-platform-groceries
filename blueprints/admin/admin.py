import flask
from flask import request, jsonify, Response
import werkzeug

from modules import file_manager, store_manager, item_manager, event_manager, service_manager, user_manager, geo_manager, order_manager, utils


admin_bp = flask.Blueprint(
    'admin', 
    __name__, 
    template_folder='templates', 
    static_folder='static', 
    url_prefix='/admin', 
    static_url_path='/static/admin'
)

@admin_bp.route('/')
@admin_bp.route('/home')
def home():
    id_token = flask.request.cookies.get("token")
    user_data = None
    my_stores = []
    my_items = []
    last_stores = []


    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)

            my_store = store_manager._load_my_stores_from_google_datastore(user_data['email'])
            
            if len(my_store) != 0:
                my_items = item_manager._load_items_from_google_datastore(
                    my_store[0]['id'])

            if len(my_store) == 0:
                return flask.redirect(flask.url_for('admin.manage_store_page'))

            if len(my_store) >= 1:
                return flask.render_template('my_store.html', user_data=user_data, my_store=my_store[0], my_items=my_items)
    
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')
    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('public.login'))


@admin_bp.route('/my_orders')
def my_orders():
    id_token = flask.request.cookies.get("token")
    user_data = None
    my_stores = []
    my_items = []
    last_stores = []


    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)

            my_store = store_manager._load_my_stores_from_google_datastore(user_data['email'])[0]
            
            orders_by_me = order_manager._load_orders_made_by_me_from_google_datastore(my_store['id'])

            orders_to_me = order_manager._load_orders_made_to_me_from_google_datastore(my_store['id'])

            return flask.render_template('my_orders.html', user_data=user_data, orders_by_me=orders_by_me, orders_to_me=orders_to_me)
    
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')
    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('public.login'))


@admin_bp.route('/my_order/<order_id>')
def my_order(order_id=None):
    id_token = flask.request.cookies.get("token")
    user_data = None

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
        
            order = order_manager._load_single_order_from_google_datastore(order_id=order_id)

            if order:
                return flask.render_template('my_order.html', user_data=user_data, order=order)
    
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')
    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('public.login'))


@admin_bp.route('/qr')
def qr():
    id_token = flask.request.cookies.get("token")
    user_data = user_manager._get_authorisation(id_token)
    
    if id_token:
        try:
            return flask.render_template(
            'qr_big.html', user_data=user_data)
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.render_template(
            'login.html')

# Stores 


@admin_bp.route('/manage_store', methods=['GET'])
def manage_store_page():
    # Verify Firebase auth.
    id_token = flask.request.cookies.get("token")
    user_data = None
    my_authorised_store = {}

    store_code_name = None
    if 'store_code_name' in flask.request.args:
        store_code_name = flask.request.args['store_code_name']
    elif 'store_code_name' in flask.request.form:
        store_code_name = flask.request.form['store_code_name']

    method = None
    if 'method' in flask.request.args:
        method = flask.request.args["method"]

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
            if method == 'edit':
                my_authorised_store = store_manager._load_store_by_code_name_if_authorised(
                    store_code_name, user_data)
                if not my_authorised_store:
                    flask.flash(
                        'No tienes permisos para modificar esta tienda, elige una tienda o crea una para empezar.')
                    return flask.redirect(flask.url_for('home'), 'warning')

        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.render_template('manage_store.html',  store_info=my_authorised_store, user_data=user_data)


@admin_bp.route("/store_engine", methods=["POST"])
def store_engine():
    id_token = flask.request.cookies.get("token")
    user_data = None

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
            store_info = store_manager._put_store_to_google_datastore_from_form_info(
                flask.request, user_data)
            flask.flash(
                u'Tienda creada o modificada correctamente!💃', 'success')
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('admin.home'))

@admin_bp.route("/store_to_group_engine", methods=["POST"])
def store_to_group_engine(item_id: str = None):
    id_token = flask.request.cookies.get("token")
    user_data = None
    item_info = {}

    store_code_name = flask.request.form['store_code_name']
    storegroup_code_name = flask.request.form['storegroup_code_name']

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
            succeed = store_manager._add_store_to_storegroup(store_code_name, storegroup_code_name)
            # return flask.jsonify(flask.request.form)
            if succeed:
                flask.flash(
                    u'Producto creado o modificado correctamente!💃', 'success')
            else:
                pass                
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect('my_store?store=' + storegroup_code_name)

@admin_bp.route("/delete_store_from_group_engine", methods=["POST"])
def delete_store_from_group_engine(item_id: str = None):
    id_token = flask.request.cookies.get("token")
    user_data = None
    item_info = {}

    store_code_name = flask.request.form['store_code_name']
    storegroup_code_name = flask.request.form['storegroup_code_name']

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
            succeed = store_manager._add_store_to_storegroup(store_code_name, storegroup_code_name, delete_mode=True)
            # return flask.jsonify(flask.request.form)
            if succeed:
                flask.flash(
                    u'Producto creado o modificado correctamente!💃', 'success')
            else:
                pass                
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect('my_store?store=' + storegroup_code_name)

@admin_bp.route("/assign_store_to_user", methods=["GET"])
def assign_store_to_user_engine(item_id: str = None):
    id_token = flask.request.cookies.get("token")
    user_data = None
    
    store_hash = flask.request.args.get('h')
    store_code_name = flask.request.args.get('s')
    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
            succeed = store_manager._assign_store_to_user(store_code_name, store_hash, user_data)
            if succeed:
                flask.flash(u'Bienvenid@! La assignación de tienda ha sido un éxito!💃', 'success')
            else:
                pass                
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('admin.home'))



# Items


@admin_bp.route('/manage_item', methods=['GET', 'POST'])
def manage_item_page():
    id_token = flask.request.cookies.get("token")
    item_info = {}
    user_data = None

    store_code_name = None
    if 'store_code_name' in flask.request.args:
        store_code_name = flask.request.args['store_code_name']
    elif 'store_code_name' in flask.request.form:
        store_code_name = flask.request.form['store_code_name']

    method = None
    if 'method' in flask.request.args:
        method = flask.request.args["method"]

    item_id = None
    if 'i' in flask.request.args:
        item_id = flask.request.args["i"]

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)

            my_authorised_store = store_manager._load_store_by_code_name_if_authorised(
                store_code_name, user_data)

            if not my_authorised_store:
                flask.flash(
                    'No tienes permisos para añadir productos a esta tienda, elige una tienda o crea una para empezar.')
                return flask.redirect(flask.url_for('admin.home'), 'warning')

            else:
                if method is None:
                    # When creating a new item from scratch
                    if flask.request.method == 'GET':
                        item_info = dict(
                            store_code_name=flask.request.args['store_code_name']
                        )

                    # When creating item from url
                    if flask.request.method == 'POST':
                        if 'product_url' in flask.request.form:
                            product_url = flask.request.form['product_url'].strip(
                            )
                            item_info = item_manager._get_product_info_form_external_page(
                                product_url)
                            item_info['store_code_name'] = my_authorised_store['code_name']

                # When editing or copying item
                if (method == 'edit' or method == 'copy'):
                    item_info = item_manager._load_single_item_from_google_datastore(
                        item_id)
                    item_info['store_code_name'] = my_authorised_store['code_name']
                    if not item_info.key.parent.name == my_authorised_store['id']:
                        flask.flash(
                            'No tienes permisos para editar este producto.')
                        return flask.redirect(flask.url_for('home'), 'warning')
                    if method == 'copy':
                        item_info['id'] = ''
                # When deleting an item
                if method == 'delete':
                    item_manager._delete_item_from_google_datastore(
                        item_id=item_id, store_id=my_authorised_store['id'])
                    return flask.redirect(flask.url_for('admin.home'))

        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))
    return flask.render_template('manage_item.html', user_data=user_data, item_info=item_info, method=method)


@admin_bp.route("/item_engine", methods=["POST"])
def item_engine(item_id: str = None):
    id_token = flask.request.cookies.get("token")
    user_data = None
    item_info = {}

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
            item_info = item_manager._put_item_to_google_datastore_from_form_info(
                flask.request, user_data)
            flask.flash(
                u'Producto creado o modificado correctamente!💃', 'success')

        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('admin.home'))


@admin_bp.route("/change_item_enabled", methods=["POST"])
def change_item_enabled(item_id: str = None):
    id_token = flask.request.cookies.get("token")
    user_data = None

    store_code_name = flask.request.form['store_code_name']
    item_id = flask.request.form['item_id']
    is_enabled =  'is_enabled' in flask.request.form
    print (is_enabled)

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)

            my_authorised_store = store_manager._load_store_by_code_name_if_authorised(
                store_code_name, user_data)

            if not my_authorised_store:
                flask.flash(
                    'No tienes permisos para modificar este producto.')
                return flask.redirect(flask.url_for('admin.home'), 'warning')
            
            else:
                succeed = item_manager._change_item_enabled(my_authorised_store, item_id, is_enabled)

                if succeed:
                    flask.flash(
                        u'Producto creado o modificado correctamente!💃', 'success')
                else:
                    pass                
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('admin.home'))


# Orders

@admin_bp.route("/order_engine", methods=["POST"])
def order_engine(order_id: str = None):
    id_token = flask.request.cookies.get("token")
    user_data = None

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
            order_manager._put_order_to_google_datastore_from_form_info(
                flask.request, user_data)
            flask.flash(
                u'Producto creado o modificado correctamente!💃', 'success')

        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')

    else:
        flask.flash('Tienes que iniciar sesión como distribuidor para poder hacer pedidos', 'warning')
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('admin.my_orders'))

@admin_bp.get("/get_order_csv/<order_id>")
def get_order_csv(order_id: str = None):

    id_token = flask.request.cookies.get("token")
    user_data = None

    if id_token:
        try:
            user_data = user_manager._get_authorisation(id_token)
        
            order = dict(order_manager._load_single_order_from_google_datastore(order_id=order_id))
            order_lines = list(order['item_lines'])

            csv = 'title, price_unit, price, qty, total\n'
            for line in order_lines:
                csv = csv + '"' + line['title'] + '",' + '"' + str(line['price_unit']) + '",' + '"' + str(line['price']) + '",' + '"' + str(line['qty']) + '",'+ '"' + str(line['total']) + '"\n'
            
            if order:
                    return Response(bytes(csv, "utf-8"),
                        mimetype="text/csv",
                        headers={"Content-disposition":
                                f"attachment; filename={order_id}.csv"})
    
        except ValueError as exc:
            flask.flash('Tu sesión ha caducado, actualiza la página', 'warning')
    else:
        return flask.redirect(flask.url_for('public.login'))

    return flask.redirect(flask.url_for('public.login'))


