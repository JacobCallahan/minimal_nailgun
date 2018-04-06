import pytest
import yaml
from nailgun.config import ServerConfig
from nailgun import entities


@pytest.fixture(scope="session", autouse=True)
def init_config():
    """Load in the nailgun config and save"""
    with open('nailgun_config.yaml') as cfg_file:
        config = yaml.load(cfg_file)
    # create a ServerConfig object and save it
    ServerConfig(
        auth=(config['SATUSER'], config['SATPASS']),
        url=config['SATHOST'],
        verify=config['VERIFY']
    ).save()  # Save to disk w/label 'default'


def test_single_entity():
    # creating entities is very easy
    org = entities.Organization(name='junk org').create()
    # you can then access their fields like an attribute
    assert org.name == 'junk org'
    org.delete()


def test_nested_entity():
    org = entities.Organization(name='nested').create()
    # you can pass an entity as another's requirement
    ak = entities.ActivationKey(
        organization=org,
        name='nested_ak'
    ).create()
    assert ak.name == 'nested_ak'
    org.delete()


def test_complex_example():
    # nailgun will fill most requirements you don't specify
    org = entities.Organization().create(create_missing=True)
    product = entities.Product(organization=org).create(create_missing=True)
    yum_repo = entities.Repository(product=product).create(create_missing=True)
    # some entities have special methods to carry out actions
    yum_repo.sync()
    content_view = entities.ContentView(organization=org).create(create_missing=True)
    # for content views, you can pass in a list of repositories
    content_view.repository = [yum_repo]
    # to make the change, call the update method
    # specifying that the repository should be updated
    content_view = content_view.update(['repository'])
    # now the repo is updated on the satellite
    assert len(content_view.repository) == 1
    content_view.publish()
    # now we can create an activation key with the content view
    ak = entities.ActivationKey(
        content_view=content_view,
        organization=org
    ).create(create_missing=True)
    # we can also search for entities, to get a list of results
    org_subscriptions = entities.Subscription(organization=org).search()
    # since the returned results are nailgun entities, we can act on them
    for subscription in org_subscriptions:
        product_ids = [
            # sometimes you may need to ignore some values that aren't returned
            prod.id for prod in subscription.read(ignore={'system'}).provided_product]
        # you can chain dot fields for entities with nested entities
        if yum_repo.product.id in product_ids:
            ak.add_subscriptions(data={
                'quantity': 1,
                'subscription_id': subscription.id,
            })
    ak_subscriptions = ak.product_content()['results']
    assert yum_repo.product.id == ak_subscriptions[0]['product']['id']
    org.delete()
