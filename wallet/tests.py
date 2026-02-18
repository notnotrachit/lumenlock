from django.test import TestCase
from django.contrib.auth.models import User
from .models import Wallet
import cryptocode
from stellar_sdk import Keypair


class WalletModelTestCase(TestCase):
    """Test cases for the Wallet model"""
    
    def setUp(self):
        """Set up test data for each test"""
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Generate test keypair and encryption data
        self.test_keypair = Keypair.random()
        self.test_password = 'secure_password_123'
        self.encrypted_secret = cryptocode.encrypt(self.test_keypair.secret, self.test_password)
    
    def test_wallet_creation_successful(self):
        """Test that a Wallet object can be created successfully"""
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=self.encrypted_secret
        )
        
        self.assertIsInstance(wallet, Wallet)
        self.assertEqual(wallet.user, self.test_user)
        self.assertIsNotNone(wallet.id)
        self.assertTrue(wallet.created_at)
        self.assertTrue(wallet.updated_at)
    
    def test_wallet_linked_to_correct_user(self):
        """Verify that the wallet is linked to the correct user"""
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=self.encrypted_secret
        )
        
        self.assertEqual(wallet.user, self.test_user)
        self.assertEqual(wallet.user.username, 'testuser')
        
        # Test relationship from user side
        user_wallets = self.test_user.wallet_set.all()
        self.assertIn(wallet, user_wallets)
    
    def test_encrypted_secret_field_not_empty(self):
        """Ensure the encrypted secret field is not empty"""
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=self.encrypted_secret
        )
        
        self.assertIsNotNone(wallet.secret_seed)
        self.assertNotEqual(wallet.secret_seed, '')
        self.assertTrue(len(wallet.secret_seed) > 0)
    
    def test_raw_secret_keys_not_stored_in_plain_text(self):
        """Add a test to ensure that raw secret keys are NOT stored in plain text"""
        raw_secret = self.test_keypair.secret
        
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=self.encrypted_secret
        )
        
        # Ensure stored secret is different from raw secret
        self.assertNotEqual(wallet.secret_seed, raw_secret)
        
        # Ensure we can decrypt it back to original
        decrypted_secret = cryptocode.decrypt(wallet.secret_seed, self.test_password)
        self.assertEqual(decrypted_secret, raw_secret)
    
    def test_wallet_string_representation(self):
        """Test the __str__ method of Wallet model"""
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=self.encrypted_secret
        )
        
        expected_str = f"{self.test_user.username}{self.test_keypair.public_key}"
        self.assertEqual(str(wallet), expected_str)
    
    def test_wallet_fields_validation(self):
        """Test that all required fields are properly set"""
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=self.encrypted_secret
        )
        
        # Test field types and constraints
        self.assertIsInstance(wallet.public_key, str)
        self.assertIsInstance(wallet.secret_seed, str)
        self.assertLessEqual(len(wallet.public_key), 56)
        # Note: Encrypted secret_seed is longer than 56 chars
        # This indicates the model field length needs to be increased
        self.assertGreater(len(wallet.secret_seed), 56)
        self.assertIsNotNone(wallet.secret_seed)


class EncryptionLogicTestCase(TestCase):
    """Test cases for the encryption logic used with Wallet model"""
    
    def setUp(self):
        """Set up test data for encryption tests"""
        self.test_keypair = Keypair.random()
        self.test_password = 'secure_test_password_123'
        self.different_password = 'different_password_456'
    
    def test_encrypt_seed_returns_different_value(self):
        """Test that encrypt_seed returns a different value than raw_seed"""
        raw_seed = self.test_keypair.secret
        encrypted_value = cryptocode.encrypt(raw_seed, self.test_password)
        
        self.assertNotEqual(encrypted_value, raw_seed)
        self.assertIsNotNone(encrypted_value)
    
    def test_encryption_output_not_none(self):
        """Ensure encryption output is not None"""
        raw_seed = self.test_keypair.secret
        encrypted_value = cryptocode.encrypt(raw_seed, self.test_password)
        
        self.assertIsNotNone(encrypted_value)
        self.assertNotEqual(encrypted_value, '')
    
    def test_different_password_produces_different_result(self):
        """Test that using a different password produces a different encrypted result"""
        raw_seed = self.test_keypair.secret
        
        encrypted_value1 = cryptocode.encrypt(raw_seed, self.test_password)
        encrypted_value2 = cryptocode.encrypt(raw_seed, self.different_password)
        
        self.assertNotEqual(encrypted_value1, encrypted_value2)
    
    def test_decrypt_returns_original_raw_seed(self):
        """Test that decrypt returns original raw_seed"""
        raw_seed = self.test_keypair.secret
        
        # Encrypt then decrypt
        encrypted_value = cryptocode.encrypt(raw_seed, self.test_password)
        decrypted_value = cryptocode.decrypt(encrypted_value, self.test_password)
        
        self.assertEqual(decrypted_value, raw_seed)
    
    def test_decrypt_with_wrong_password_fails(self):
        """Test that decryption with wrong password fails"""
        raw_seed = self.test_keypair.secret
        
        encrypted_value = cryptocode.encrypt(raw_seed, self.test_password)
        decrypted_value = cryptocode.decrypt(encrypted_value, self.different_password)
        
        # cryptocode returns False for failed decryption
        self.assertFalse(decrypted_value)
        self.assertNotEqual(decrypted_value, raw_seed)


class WalletModelAdvancedTestCase(TestCase):
    """Advanced test cases with edge cases and invalid inputs"""
    
    def setUp(self):
        """Set up test data for advanced tests"""
        self.test_user = User.objects.create_user(
            username='advanceduser',
            password='testpass123',
            email='advanced@example.com'
        )
        self.test_keypair = Keypair.random()
    
    def test_wallet_cascade_deletion(self):
        """Test that wallet is deleted when user is deleted (CASCADE)"""
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=cryptocode.encrypt(self.test_keypair.secret, 'password'),
        )
        wallet_id = wallet.id
        
        # Delete user
        self.test_user.delete()
        
        # Wallet should be deleted due to CASCADE
        with self.assertRaises(Wallet.DoesNotExist):
            Wallet.objects.get(id=wallet_id)
    
    def test_multiple_wallets_per_user(self):
        """Test that multiple wallets can be created for same user (if allowed)"""
        keypair1 = Keypair.random()
        keypair2 = Keypair.random()
        
        wallet1 = Wallet.objects.create(
            user=self.test_user,
            public_key=keypair1.public_key,
            secret_seed=cryptocode.encrypt(keypair1.secret, 'password1')
        )
        
        wallet2 = Wallet.objects.create(
            user=self.test_user,
            public_key=keypair2.public_key,
            secret_seed=cryptocode.encrypt(keypair2.secret, 'password2')
        )
        
        user_wallets = Wallet.objects.filter(user=self.test_user)
        self.assertEqual(user_wallets.count(), 2)
        self.assertIn(wallet1, user_wallets)
        self.assertIn(wallet2, user_wallets)
    
    def test_empty_encryption_password(self):
        """Test encryption behavior with empty password"""
        raw_seed = self.test_keypair.secret
        
        # Test with empty string password
        encrypted_value = cryptocode.encrypt(raw_seed, '')
        self.assertIsNotNone(encrypted_value)
        
        # Should be able to decrypt with same empty password
        decrypted_value = cryptocode.decrypt(encrypted_value, '')
        self.assertEqual(decrypted_value, raw_seed)
    
    def test_wallet_timestamps(self):
        """Test that created_at and updated_at timestamps work correctly"""
        wallet = Wallet.objects.create(
            user=self.test_user,
            public_key=self.test_keypair.public_key,
            secret_seed=cryptocode.encrypt(self.test_keypair.secret, 'password')
        )
        
        created_time = wallet.created_at
        updated_time = wallet.updated_at
        
        # Initially, both should be the same
        self.assertAlmostEqual(
            created_time.timestamp(), 
            updated_time.timestamp(), 
            places=0  # Within 1 second
        )
        
        # Update wallet and check updated_at changes
        import time
        time.sleep(1)  # Ensure time difference
        
        wallet.public_key = Keypair.random().public_key
        wallet.save()
        
        # created_at should remain same, updated_at should change
        wallet.refresh_from_db()
        self.assertEqual(wallet.created_at, created_time)
        self.assertGreater(wallet.updated_at, updated_time)
